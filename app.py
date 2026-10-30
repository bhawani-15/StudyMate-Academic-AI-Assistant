"""StudyMate — Complete Academic AI Study Platform.

Architecture:
- Presentation: Clean modular views (Landing, Auth, Dashboard, Chat, Library, History, Settings, Profile, Help)
- Theming: Real dynamic Light / Dark mode engine
- Backend: SQLite persistence, bcrypt security, Pinecone vector search, Groq LLM generation
"""

from pathlib import Path
import hashlib
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

import auth
import database
from ui.theme import apply_theme
from ui.views.landing import render_landing_page
from ui.views.auth_view import render_auth_view
from ui.views.dashboard import render_dashboard
from ui.views.chat import render_chat_view
from ui.views.library import render_library_view
from ui.views.history import render_history_view
from ui.views.settings import render_settings_view
from ui.views.profile import render_profile_view
from ui.views.help_view import render_help_view

# ----------------------------------------------------------------------------
# 1. Environment & Setup
# ----------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent
PDF_DIR = PROJECT_DIR / "Data"

load_dotenv(PROJECT_DIR / ".env")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "academic-rag")

# Initialize database tables
database.init_db()

st.set_page_config(
    page_title="StudyMate — Academic AI Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# 2. Session State Initialization
# ----------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = {}

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Inject dynamic theme stylesheet
st.markdown(apply_theme(st.session_state.theme), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. Document Ingestion & Pinecone Management (UNTOUCHED Core RAG Logic)
# ----------------------------------------------------------------------------
@st.cache_resource
def _get_embeddings():
    """HuggingFace sentence-transformer embeddings (384 dimensions)."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def _ingest_pdf(uploaded_file, user_id):
    """Save PDF, split text chunks, and upsert vectors to Pinecone index."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    file_bytes = uploaded_file.getvalue()
    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    file_hash = hashlib.sha256(file_bytes).hexdigest()[:16]
    safe_name = Path(uploaded_file.name).name
    destination = PDF_DIR / safe_name
    destination.write_bytes(file_bytes)

    loader = PyMuPDFLoader(str(destination))
    documents = loader.load()

    if not documents:
        raise ValueError(f"No readable pages were found in {safe_name}.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError(f"No text chunks could be created from {safe_name}.")

    for chunk in chunks:
        chunk.metadata["source"] = str(destination)
        chunk.metadata["file_name"] = safe_name
        chunk.metadata["document_id"] = file_hash

    ids = [f"{file_hash}-{index}" for index in range(len(chunks))]

    vector_store = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=_get_embeddings(),
    )
    vector_store.add_documents(documents=chunks, ids=ids)

    # Persist document metadata in SQLite
    database.create_document(
        doc_id=file_hash,
        user_id=user_id,
        file_name=safe_name,
        file_path=str(destination),
        file_size=len(file_bytes),
        page_count=len(documents),
        chunk_count=len(chunks),
    )

    _sync_user_documents(user_id)
    return len(documents), len(chunks), safe_name


def _sync_user_documents(user_id):
    """Sync active document registry from SQLite for the authenticated user."""
    docs = database.get_documents_by_user(user_id)
    st.session_state.uploaded_documents = {
        doc["file_name"]: doc["id"] for doc in docs
    }


def _delete_document(doc_id):
    """Delete document from SQLite and prune vectors from Pinecone if no other user has it."""
    if not st.session_state.user:
        return

    user_id = st.session_state.user["id"]
    doc = database.get_document_by_id(doc_id, user_id=user_id)
    chunk_count = doc.get("chunk_count", 0) if doc else 0

    database.delete_document(doc_id, user_id=user_id)
    _sync_user_documents(user_id)

    # Only prune vectors from Pinecone if no other user has this document in SQLite
    remaining = database.get_document_by_id(doc_id)
    if not remaining and chunk_count > 0:
        try:
            chunk_ids = [f"{doc_id}-{i}" for i in range(chunk_count)]
            vector_store = PineconeVectorStore(
                index_name=PINECONE_INDEX_NAME,
                embedding=_get_embeddings(),
            )
            vector_store.delete(ids=chunk_ids)
        except Exception:
            pass


def _start_chat_with_docs(doc_ids):
    """Start a fresh chat targeting specific document IDs."""
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.page = "chat"


# ----------------------------------------------------------------------------
# 4. Global Action Callbacks
# ----------------------------------------------------------------------------
def _start_new_chat():
    """Start a fresh conversation."""
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.page = "chat"


def _open_conversation(convo_id):
    """Load an existing conversation from SQLite."""
    st.session_state.current_conversation_id = convo_id
    st.session_state.messages = database.get_messages_by_conversation(convo_id)
    st.session_state.page = "chat"


def _delete_conversation(convo_id):
    """Delete a conversation container and its messages."""
    if st.session_state.user:
        database.delete_conversation(convo_id, user_id=st.session_state.user["id"])
    if st.session_state.current_conversation_id == convo_id:
        st.session_state.current_conversation_id = None
        st.session_state.messages = []


def _logout():
    """Clear session and return to landing page."""
    auth.logout_user()
    st.session_state.page = "landing"


# ----------------------------------------------------------------------------
# 5. PUBLIC VIEWS (When User is NOT Authenticated)
# ----------------------------------------------------------------------------
if not auth.is_authenticated():
    # Hide sidebar when on public pages
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.page == "auth":
        render_auth_view(_sync_user_documents)
    else:
        render_landing_page()
    st.stop()


# ----------------------------------------------------------------------------
# 6. AUTHENTICATED WORKSPACE SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
current_user = auth.get_current_user()

# Keep document library synchronized in session state
if not st.session_state.uploaded_documents:
    _sync_user_documents(current_user["id"])

with st.sidebar:
    # Brand Identity
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.6rem; padding: 0.2rem 0 1rem; border-bottom: 1px solid var(--border-color);">
            <div style="
                background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
                color: #FFFFFF;
                width: 34px;
                height: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.15rem;
            ">📚</div>
            <div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.25rem; font-weight: 800; color: var(--text-primary); line-height: 1;">StudyMate</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 500;">Academic AI Workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)

    # Primary Action: + New Chat
    if st.button("➕ New Chat", key="sb_primary_new_chat", type="primary", use_container_width=True):
        _start_new_chat()
        st.rerun()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Navigation Menu Items
    current_p = st.session_state.page

    nav_items = [
        ("📊 Dashboard", "dashboard"),
        ("💬 AI Study Chat", "chat"),
        ("📚 Study Library", "library"),
        ("🕒 History", "history"),
        ("🎓 Profile", "profile"),
        ("⚙️ Settings", "settings"),
        ("❓ About & Help", "help"),
    ]

    for label, target_page in nav_items:
        is_active = (current_p == target_page)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_to_{target_page}", type=btn_type, use_container_width=True):
            st.session_state.page = target_page
            st.rerun()

    # Quick Upload Widget in Sidebar
    with st.expander("📄 Quick Add Material", expanded=False):
        sb_quick_file = st.file_uploader(
            "Upload course PDF",
            type=["pdf"],
            key="sb_quick_doc_uploader",
            label_visibility="collapsed",
            help="Upload a PDF directly to your Study Library",
        )
        if sb_quick_file:
            if st.button("Add to Library", key="sb_btn_quick_upload", type="primary", use_container_width=True):
                with st.spinner("Processing PDF..."):
                    try:
                        _ingest_pdf(sb_quick_file, current_user["id"])
                        _sync_user_documents(current_user["id"])
                        st.success("Added to library!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error: {exc}")

    st.markdown("<hr style='margin: 1.2rem 0 0.8rem; border-color: var(--border-color);'>", unsafe_allow_html=True)

    # Theme Switcher Pill in Sidebar
    theme = st.session_state.get("theme", "light")
    _t_lbl = "🌙 Dark Mode" if theme == "light" else "☀ Light Mode"
    if st.button(_t_lbl, key="sb_theme_toggle_btn", use_container_width=True):
        st.session_state.theme = "dark" if theme == "light" else "light"
        st.rerun()

    # User Profile Pill & Log out
    st.markdown(
        f"""
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 0.55rem 0.75rem;
            margin: 0.8rem 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <div style="font-weight: 700; font-size: 0.85rem; color: var(--text-primary);">{current_user['username']}</div>
                <div style="font-size: 0.72rem; color: var(--text-muted);">{current_user['email'][:20]}...</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Log out", key="sb_logout_btn", use_container_width=True):
        _logout()
        st.rerun()


# ----------------------------------------------------------------------------
# 7. AUTHENTICATED VIEW DISPATCHER
# ----------------------------------------------------------------------------
active_page = st.session_state.page

if active_page == "dashboard":
    render_dashboard(current_user, _start_new_chat, _open_conversation)

elif active_page == "chat":
    render_chat_view(current_user, _start_new_chat, _sync_user_documents, _ingest_pdf)

elif active_page == "library":
    render_library_view(current_user, _ingest_pdf, _delete_document, _start_chat_with_docs)

elif active_page == "history":
    render_history_view(current_user, _open_conversation, _delete_conversation)

elif active_page == "profile":
    render_profile_view(current_user, _logout)

elif active_page == "settings":
    render_settings_view(current_user, _logout)

elif active_page == "help":
    render_help_view()

else:
    # Default fallback
    render_dashboard(current_user, _start_new_chat, _open_conversation)