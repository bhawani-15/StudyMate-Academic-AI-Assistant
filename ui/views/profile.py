"""User profile view for StudyMate."""

from typing import Callable
import streamlit as st
import database
from ui.components import render_stat_card


def render_profile_view(user, logout_callback: Callable):
    """Render the user profile card and activity statistics."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent);">Account</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0;">
                🎓 Profile
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Profile Badge Card
    st.markdown(
        f"""
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1.2rem;
            box-shadow: var(--shadow-sm);
        ">
            <div style="
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
                color: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                font-weight: 700;
            ">
                {user['username'][:1].upper()}
            </div>
            <div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">{user['username']}</div>
                <div style="font-size: 0.92rem; color: var(--text-muted);">{user['email']}</div>
                <div style="font-size: 0.78rem; color: var(--text-light); margin-top: 0.2rem;">Role: Student / Academic Researcher</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_convos = database.get_conversations_by_user(user["id"])
    user_docs = database.get_documents_by_user(user["id"])

    s1, s2 = st.columns(2)
    with s1:
        render_stat_card("💬", "Saved Conversations", str(len(user_convos)))
    with s2:
        render_stat_card("📚", "Uploaded Materials", str(len(user_docs)))

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    if st.button("Log out", key="profile_logout_btn", use_container_width=False):
        logout_callback()
        st.rerun()
