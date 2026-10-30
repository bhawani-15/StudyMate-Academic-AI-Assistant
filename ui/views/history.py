"""Dedicated conversation history page for StudyMate."""

from typing import Callable
import streamlit as st
import database
from ui.components import render_stat_card, render_empty_state


def render_history_view(user, open_conversation_callback: Callable, delete_conversation_callback: Callable):
    """Render the full searchable conversation history catalog."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent);">Archive</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0;">
                💬 Conversation History
            </h1>
            <p style="font-size: 1rem; color: var(--text-secondary); margin-top: 0.35rem;">
                Browse, search, and manage your previous academic study conversations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_convos = database.get_conversations_by_user(user["id"])

    # Search Bar
    search_q = st.text_input("Search conversations", placeholder="Search past topics by title...", label_visibility="collapsed", key="history_search_input")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    if all_convos:
        filtered = [
            c for c in all_convos
            if not search_q or search_q.lower() in c["title"].lower()
        ]

        if filtered:
            for convo in filtered:
                time_str = convo.get("updated_at", "")[:16]
                messages = database.get_messages_by_conversation(convo["id"])
                msg_count = len(messages)

                with st.container():
                    _c_info, _c_act = st.columns([4.2, 1.6])
                    with _c_info:
                        st.markdown(
                            f"""
                            <div style="
                                background: var(--bg-surface);
                                border: 1px solid var(--border-color);
                                border-radius: 12px;
                                padding: 1rem 1.2rem;
                                box-shadow: var(--shadow-sm);
                            ">
                                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.05rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                                    💬 {convo['title']}
                                </div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; gap: 1.5rem;">
                                    <span>Last Active: <strong>{time_str}</strong></span>
                                    <span>Messages: <strong>{msg_count}</strong></span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with _c_act:
                        _b_open, _b_del = st.columns([1.6, 1])
                        with _b_open:
                            if st.button("Open", key=f"hist_open_{convo['id']}", use_container_width=True):
                                open_conversation_callback(convo["id"])
                                st.session_state.page = "chat"
                                st.rerun()
                        with _b_del:
                            if st.button("🗑️", key=f"hist_del_{convo['id']}", help="Delete conversation", use_container_width=True):
                                delete_conversation_callback(convo["id"])
                                st.rerun()

                    st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("No conversations match your search.")
    else:
        render_empty_state(
            icon="💬",
            title="No conversations saved yet",
            description="When you ask questions in StudyMate, your academic conversations are automatically saved here for later review.",
            hint="Go to AI Study Chat or Dashboard to start your first chat.",
        )
