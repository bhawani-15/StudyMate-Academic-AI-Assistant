"""User workspace dashboard for StudyMate."""

from datetime import datetime
import streamlit as st
import database
from ui.components import render_stat_card


def render_dashboard(user, start_new_chat_callback, open_conversation_callback):
    """Render the user personal workspace dashboard."""
    # Greeting based on time
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")

    # Header section
    st.markdown(
        f"""
        <div style="margin-bottom: 1.8rem;">
            <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent); margin-bottom: 0.2rem;">Workspace Overview</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.4rem; font-weight: 800; color: var(--text-primary); margin: 0; line-height: 1.2;">
                {greeting}, {user['username']} 👋
            </h1>
            <p style="font-size: 1.05rem; color: var(--text-secondary); margin-top: 0.4rem;">
                Ready to continue learning? Your study materials are organized and ready for questions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Ask Bar (Direct jump into chat with question)
    with st.form("dash_quick_ask_form", clear_on_submit=True):
        _in_c, _btn_c = st.columns([5.5, 1.2])
        with _in_c:
            quick_q = st.text_input(
                "Quick Ask",
                placeholder="Ask StudyMate anything from your study materials...",
                label_visibility="collapsed",
                key="dash_quick_ask_input",
            )
        with _btn_c:
            quick_submit = st.form_submit_button("Ask →", type="primary", use_container_width=True)

        if quick_submit and quick_q.strip():
            st.session_state.pending_prompt = quick_q.strip()
            start_new_chat_callback()
            st.session_state.page = "chat"
            st.rerun()

    st.markdown("<div style='margin-top: 1.6rem;'></div>", unsafe_allow_html=True)

    # 3 Quick Action Buttons
    _qa1, _qa2, _qa3 = st.columns(3)
    with _qa1:
        if st.button("💬 Start New Chat", key="qa_btn_new_chat", type="primary", use_container_width=True):
            start_new_chat_callback()
            st.session_state.page = "chat"
            st.rerun()
    with _qa2:
        if st.button("📄 Upload Material", key="qa_btn_upload", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()
    with _qa3:
        if st.button("📚 Browse Library", key="qa_btn_library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Statistics Tiles
    user_convos = database.get_conversations_by_user(user["id"])
    user_docs = database.get_documents_by_user(user["id"])
    total_sections = sum(d.get("chunk_count", 0) for d in user_docs)

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        render_stat_card("📚", "Study Documents", str(len(user_docs)), "Ready for learning")
    with stat2:
        render_stat_card("💬", "Conversations", str(len(user_convos)), "Saved academic chats")
    with stat3:
        render_stat_card("🔖", "Study Sections", str(total_sections), "Organized for quick answers")

    st.markdown("<div style='margin-top: 2.2rem;'></div>", unsafe_allow_html=True)

    # Two-Column Activity Grid
    _col_chats, _col_docs = st.columns([1.2, 1.0], gap="large")

    with _col_chats:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.6rem; margin-bottom: 1rem;">
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">💬 Recent Conversations</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_convos:
            for convo in user_convos[:5]:
                with st.container():
                    _c_info, _c_act = st.columns([4, 1.2])
                    with _c_info:
                        display_title = convo["title"][:42] + ("..." if len(convo["title"]) > 42 else "")
                        time_str = convo.get("updated_at", "")[:16]
                        st.markdown(
                            f"""
                            <div style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary); margin-bottom: 0.15rem;">
                                {display_title}
                            </div>
                            <div style="font-size: 0.78rem; color: var(--text-muted);">{time_str}</div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with _c_act:
                        if st.button("Resume", key=f"dash_open_convo_{convo['id']}", use_container_width=True):
                            open_conversation_callback(convo["id"])
                            st.session_state.page = "chat"
                            st.rerun()
                    st.markdown("<hr style='margin: 0.4rem 0 0.7rem; border-color: var(--border-subtle);'>", unsafe_allow_html=True)

            if len(user_convos) > 5:
                if st.button("View All Conversations →", key="dash_view_all_chats", use_container_width=True):
                    st.session_state.page = "history"
                    st.rerun()
        else:
            st.info("No saved conversations yet. Use 'Start New Chat' above to ask your first question!")

    with _col_docs:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.6rem; margin-bottom: 1rem;">
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">📄 Active Study Materials</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_docs:
            for doc in user_docs[:5]:
                kb = round(doc.get("file_size", 0) / 1024, 1)
                chunks = doc.get("chunk_count", 0)
                st.markdown(
                    f"""
                    <div style="
                        background: var(--bg-surface);
                        border: 1px solid var(--border-color);
                        border-radius: 12px;
                        padding: 0.75rem 0.9rem;
                        margin-bottom: 0.6rem;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <div>
                            <div style="font-weight: 600; font-size: 0.92rem; color: var(--text-primary);">📄 {doc['file_name']}</div>
                            <div style="font-size: 0.76rem; color: var(--text-muted);">{kb} KB • {chunks} study sections</div>
                        </div>
                        <span style="background: var(--badge-bg); color: var(--badge-text); font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 6px;">Ready</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if len(user_docs) > 5:
                if st.button("Manage Library →", key="dash_manage_library", use_container_width=True):
                    st.session_state.page = "library"
                    st.rerun()
        else:
            st.caption("No study materials uploaded yet. Go to Study Library to upload your first textbook or lecture notes.")
