"""Study Library view for managing academic course notes and textbooks."""

from typing import Callable
import streamlit as st
import database
from ui.components import render_stat_card, render_empty_state


def render_library_view(user, ingest_pdf_callback: Callable, delete_document_callback: Callable, start_chat_with_docs_callback: Callable):
    """Render the central study library management interface."""
    st.markdown(
        """
        <div style="margin-bottom: 1.4rem;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent);">Study Materials</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0;">
                📚 Study Library
            </h1>
            <p style="font-size: 1rem; color: var(--text-secondary); margin-top: 0.35rem;">
                Upload, organize, and manage your textbooks, lecture notes, and course handouts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Flash Status Notification if present
    if "lib_flash" in st.session_state and st.session_state.lib_flash:
        flash = st.session_state.lib_flash
        f_type = flash.get("type", "info")
        f_msg = flash.get("msg", "")
        if f_type == "success":
            st.success(f_msg)
        elif f_type == "error":
            st.error(f_msg)
        else:
            st.info(f_msg)
        st.session_state.lib_flash = None

    # Prominent Upload Card
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--shadow-sm);
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span style="font-size: 1.25rem;">➕</span>
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">
                    Add New Study Material
                </span>
            </div>
            <div style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 0.6rem;">
                Upload textbooks, lecture slides, syllabus handouts, or notes in PDF format.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="lib_file_uploader",
        help="Upload course textbooks, notes, or lecture PDFs.",
    )

    if uploaded_files:
        _u_info, _u_btn = st.columns([3.8, 1.4])
        with _u_info:
            file_names = ", ".join(f.name for f in uploaded_files)
            st.caption(f"📄 Selected {len(uploaded_files)} file(s): **{file_names}**")
        with _u_btn:
            if st.button("➕ Add to Study Materials", type="primary", key="lib_btn_upload", use_container_width=True):
                with st.spinner("Preparing and organizing your study materials..."):
                    success_count = 0
                    errors = []
                    for file in uploaded_files:
                        try:
                            pages, chunks, fname = ingest_pdf_callback(file, user["id"])
                            success_count += 1
                        except Exception as exc:
                            errors.append(f"{file.name}: {str(exc)}")

                    if success_count > 0:
                        msg = f"Successfully added {success_count} document{'s' if success_count > 1 else ''} to your Study Library! You can now ask questions about them."
                        if errors:
                            msg += f" (Note: {'; '.join(errors)})"
                        st.session_state.lib_flash = {"type": "success", "msg": msg}
                    else:
                        st.session_state.lib_flash = {"type": "error", "msg": "Could not add files: " + "; ".join(errors)}
                st.rerun()

    st.markdown("<div style='margin-top: 1.4rem;'></div>", unsafe_allow_html=True)

    # Fetch User Documents from Database
    user_docs = database.get_documents_by_user(user["id"])

    # Library Summary Stats
    total_pages = sum(d.get("page_count", 0) for d in user_docs)
    total_sections = sum(d.get("chunk_count", 0) for d in user_docs)
    total_mb = round(sum(d.get("file_size", 0) for d in user_docs) / (1024 * 1024), 2)

    s1, s2, s3 = st.columns(3)
    with s1:
        render_stat_card("📄", "Total Documents", str(len(user_docs)))
    with s2:
        render_stat_card("📑", "Total Pages", str(total_pages))
    with s3:
        render_stat_card("🔖", "Study Sections", str(total_sections), f"{total_mb} MB on disk")

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Document Search & Filter
    _search_col, _ = st.columns([3, 2])
    with _search_col:
        search_query = st.text_input("Filter materials", placeholder="Search by document name...", label_visibility="collapsed", key="lib_search_input")

    # Document List
    if user_docs:
        filtered_docs = [
            d for d in user_docs
            if not search_query or search_query.lower() in d["file_name"].lower()
        ]

        if filtered_docs:
            for doc in filtered_docs:
                kb = round(doc.get("file_size", 0) / 1024, 1)
                pages = doc.get("page_count", 0)
                sections = doc.get("chunk_count", 0)
                date_str = doc.get("created_at", "")[:16]

                with st.container():
                    _c_card, _c_actions = st.columns([4.2, 1.8])
                    with _c_card:
                        st.markdown(
                            f"""
                            <div style="
                                background: var(--bg-surface);
                                border: 1px solid var(--border-color);
                                border-radius: 12px;
                                padding: 1rem 1.2rem;
                                box-shadow: var(--shadow-sm);
                            ">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                    <span style="font-size: 1.25rem;">📄</span>
                                    <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.05rem; color: var(--text-primary);">{doc['file_name']}</span>
                                    <span style="background: var(--badge-bg); color: var(--badge-text); font-size: 0.72rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px;">PDF</span>
                                </div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; gap: 1.2rem; margin-top: 0.4rem;">
                                    <span>Size: <strong>{kb} KB</strong></span>
                                    <span>Pages: <strong>{pages}</strong></span>
                                    <span>Study Sections: <strong>{sections}</strong></span>
                                    <span>Added: <strong>{date_str}</strong></span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with _c_actions:
                        _b1, _b2 = st.columns([2.0, 1])
                        with _b1:
                            if st.button("💬 Ask Questions", key=f"lib_query_{doc['id']}", use_container_width=True):
                                start_chat_with_docs_callback([doc["id"]])
                                st.session_state.page = "chat"
                                st.rerun()
                        with _b2:
                            if st.button("🗑️", key=f"lib_del_{doc['id']}", help="Delete document from your library", use_container_width=True):
                                delete_document_callback(doc["id"])
                                st.rerun()

                    st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("No documents match your search query.")
    else:
        render_empty_state(
            icon="📚",
            title="Your Study Library is empty",
            description="Upload your course textbooks, lecture slides, or study guides above to begin asking questions and getting verified answers.",
            hint="Choose a PDF file above and click '➕ Add to Study Materials'.",
        )
