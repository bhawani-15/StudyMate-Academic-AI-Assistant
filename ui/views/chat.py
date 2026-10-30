"""AI Study Chat view for StudyMate."""

from typing import Callable, List, Optional
import streamlit as st
import database
from rag_pipeline import (
    ConfigurationError,
    GenerationError,
    RetrievalError,
    ask_question,
)
from ui.components import format_latex, render_source_passages


def render_chat_view(
    user,
    start_new_chat_callback: Callable,
    sync_documents_callback: Callable,
    ingest_pdf_callback: Optional[Callable] = None,
):
    """Render the core conversational study interface."""
    current_convo = (
        database.get_conversation_by_id(st.session_state.current_conversation_id)
        if st.session_state.current_conversation_id
        else None
    )
    title_text = current_convo["title"] if current_convo else "New Study Conversation"

    # Chat Header Bar
    _nav_l, _nav_mid, _nav_r = st.columns([1.3, 3.8, 1.3])
    with _nav_l:
        if st.button("← Dashboard", key="chat_back_dash", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with _nav_mid:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary); line-height: 1.2;">
                    💬 {title_text}
                </div>
                <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 0.15rem;">
                    Answers verified strictly against your study materials
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with _nav_r:
        if st.button("+ New Chat", key="chat_btn_new_chat", on_click=start_new_chat_callback, use_container_width=True):
            st.rerun()

    st.markdown("<hr style='margin: 0.6rem 0 1.2rem; border-color: var(--border-color);'>", unsafe_allow_html=True)

    # Optional quick upload expander right inside chat view
    if ingest_pdf_callback:
        with st.expander("📄 Add Study Material to Library", expanded=False):
            chat_quick_files = st.file_uploader(
                "Upload textbook or lecture PDF",
                type=["pdf"],
                accept_multiple_files=True,
                key="chat_inline_uploader",
                help="Quickly add study material directly while in chat.",
            )
            if chat_quick_files:
                if st.button("➕ Add to Study Materials", key="chat_inline_upload_btn", type="primary"):
                    with st.spinner("Preparing your study materials..."):
                        added = 0
                        for f in chat_quick_files:
                            try:
                                ingest_pdf_callback(f, user["id"])
                                added += 1
                            except Exception as e:
                                st.error(f"Error adding {f.name}: {e}")
                    if added > 0:
                        sync_documents_callback(user["id"])
                        st.success(f"Added {added} document(s) to your study library!")
                        st.rerun()

    # Empty State & Prompt Inspiration
    if not st.session_state.messages:
        active_docs = list(st.session_state.uploaded_documents.keys())

        if not active_docs:
            # Welcoming prompt when user has zero study materials
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 2.8rem 1.5rem 2rem;
                    background: var(--bg-surface);
                    border: 2px dashed var(--border-color);
                    border-radius: 18px;
                    margin: 1.2rem 0 1.8rem;
                ">
                    <div style="font-size: 2.8rem; margin-bottom: 0.4rem;">📚</div>
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.35rem;">
                        Welcome to AI Study Chat
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.95rem; max-width: 520px; margin: 0 auto 1.4rem;">
                        To begin studying, add your textbook, lecture notes, or syllabus PDF below. StudyMate will answer your questions using verified facts from your materials.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if ingest_pdf_callback:
                chat_start_files = st.file_uploader(
                    "Choose PDF study materials",
                    type=["pdf"],
                    accept_multiple_files=True,
                    label_visibility="collapsed",
                    key="chat_empty_state_uploader",
                )
                if chat_start_files:
                    if st.button("➕ Add & Start Studying", key="chat_first_upload_btn", type="primary", use_container_width=True):
                        with st.spinner("Preparing your study materials..."):
                            for f in chat_start_files:
                                try:
                                    ingest_pdf_callback(f, user["id"])
                                except Exception as e:
                                    st.error(f"Error adding {f.name}: {e}")
                        sync_documents_callback(user["id"])
                        st.rerun()

        else:
            doc_summary = ", ".join(active_docs[:2])
            if len(active_docs) > 2:
                doc_summary += f" +{len(active_docs) - 2} more"

            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 3rem 1.5rem 2.2rem;
                    background: var(--bg-surface);
                    border: 1px dashed var(--border-color);
                    border-radius: 18px;
                    margin: 1.5rem 0 2rem;
                ">
                    <div style="font-size: 2.8rem; margin-bottom: 0.4rem;">📚</div>
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.35rem;">
                        Ready to learn?
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.95rem; max-width: 520px; margin: 0 auto 1.4rem;">
                        Ask anything about your study materials. Every response includes page-level citations.
                    </div>
                    <div style="display: inline-flex; align-items: center; gap: 0.4rem; background: var(--bg-subtle); padding: 0.35rem 0.8rem; border-radius: 20px; font-size: 0.8rem; color: var(--text-muted);">
                        <span>📄 Active Materials:</span>
                        <strong style="color: var(--text-primary);">{doc_summary}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 0.6rem;">
                    Try asking:
                </div>
                """,
                unsafe_allow_html=True,
            )

            _s_c1, _s_c2 = st.columns(2)
            with _s_c1:
                if st.button("❓ What does the uncertainty principle state?", key="sample_q1", use_container_width=True):
                    st.session_state.pending_prompt = "What does the uncertainty principle state?"
                    st.rerun()
            with _s_c2:
                if st.button("❓ Explain the key concepts in this material.", key="sample_q2", use_container_width=True):
                    st.session_state.pending_prompt = "Explain the key concepts in this material."
                    st.rerun()

    # Render Conversation Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown('<span class="sm-user-flag"></span>', unsafe_allow_html=True)
                st.markdown(format_latex(msg["content"]))
            else:
                st.markdown(
                    """
                    <div class="sm-ans-badge">
                        <span>✨ Grounded Academic Answer</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(format_latex(msg["content"]))
                if msg.get("sources"):
                    render_source_passages(msg["sources"])

    # Handle pending prompt from quick actions or sample chips
    initial_value = ""
    auto_trigger = False
    if st.session_state.get("pending_prompt"):
        initial_value = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        auto_trigger = True

    # Question Input Form
    with st.form("chat_composer_form", clear_on_submit=True):
        _in_col, _btn_col = st.columns([5.5, 1.1])
        with _in_col:
            user_input = st.text_input(
                "Ask question",
                value=initial_value if not auto_trigger else "",
                placeholder="Ask a question about your study material...",
                label_visibility="collapsed",
                key="chat_composer_input",
            )
        with _btn_col:
            submit_ask = st.form_submit_button("Send →", type="primary", use_container_width=True)

    # Process query
    question_to_process = initial_value if auto_trigger else (user_input.strip() if submit_ask else None)

    if question_to_process:
        # Create conversation container in SQLite if fresh
        if not st.session_state.current_conversation_id:
            title = question_to_process[:38] + ("..." if len(question_to_process) > 38 else "")
            new_convo = database.create_conversation(user_id=user["id"], title=title)
            st.session_state.current_conversation_id = new_convo["id"]

        convo_id = st.session_state.current_conversation_id

        # 1. Save user question
        database.create_message(conversation_id=convo_id, role="user", content=question_to_process)
        st.session_state.messages.append({"role": "user", "content": question_to_process})

        # 2. Check active documents
        active_doc_ids = list(st.session_state.uploaded_documents.values())
        if not active_doc_ids:
            no_doc_msg = (
                "No study materials were found in your library. Please use the 'Add Study Material' "
                "button above or go to the Study Library to upload your course PDFs before asking questions."
            )
            database.create_message(conversation_id=convo_id, role="assistant", content=no_doc_msg)
            st.session_state.messages.append({"role": "assistant", "content": no_doc_msg, "sources": []})
        else:
            with st.spinner("🔎 Searching your study material and generating grounded answer..."):
                try:
                    answer, source_docs = ask_question(question_to_process, document_ids=active_doc_ids)

                    source_data = [
                        {
                            "page_content": doc.page_content if hasattr(doc, "page_content") else doc.get("page_content", ""),
                            "metadata": doc.metadata if hasattr(doc, "metadata") else doc.get("metadata", {}),
                        }
                        for doc in source_docs
                    ]

                    # 3. Save assistant response
                    database.create_message(conversation_id=convo_id, role="assistant", content=answer, sources=source_data)
                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": source_data})

                except ValueError as exc:
                    err_msg = str(exc)
                    database.create_message(conversation_id=convo_id, role="assistant", content=err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
                except ConfigurationError:
                    err_msg = "Study service credentials are not configured in system settings. Please contact support."
                    database.create_message(conversation_id=convo_id, role="assistant", content=err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
                except RetrievalError as exc:
                    err_msg = f"Search Error: {exc}"
                    database.create_message(conversation_id=convo_id, role="assistant", content=err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
                except GenerationError as exc:
                    err_msg = f"Answer Generation Error: {exc}"
                    database.create_message(conversation_id=convo_id, role="assistant", content=err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
                except Exception as exc:
                    err_msg = f"Unexpected Error: {exc}"
                    database.create_message(conversation_id=convo_id, role="assistant", content=err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})

        st.rerun()
