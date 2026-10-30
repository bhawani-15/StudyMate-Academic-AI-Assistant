"""Settings view for StudyMate with theme switcher and account preferences."""

from typing import Callable
import streamlit as st


def render_settings_view(user, logout_callback: Callable):
    """Render application settings, appearance toggle, and account information."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent);">Preferences</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0;">
                ⚙️ Settings
            </h1>
            <p style="font-size: 1rem; color: var(--text-secondary); margin-top: 0.35rem;">
                Customize your appearance theme, inspect system information, and manage your account.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Appearance / Theme Section
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.4rem;">
                🎨 Appearance
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1rem;">
                Switch between Light and Dark themes across the entire application interface.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_theme = st.session_state.get("theme", "light")
    _c_light, _c_dark = st.columns(2)
    with _c_light:
        is_light = (current_theme == "light")
        if st.button("☀ Light Mode", key="set_theme_light", type="primary" if is_light else "secondary", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()
    with _c_dark:
        is_dark = (current_theme == "dark")
        if st.button("🌙 Dark Mode", key="set_theme_dark", type="primary" if is_dark else "secondary", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Account Information Section
    st.markdown(
        f"""
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.4rem;">
                👤 Account Information
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1rem;">
                Manage your credentials and authentication session.
            </p>
            <div style="font-size: 0.9rem; line-height: 1.8;">
                <div>Username: <strong>{user['username']}</strong></div>
                <div>Email: <strong>{user['email']}</strong></div>
                <div>User ID: <code>{user['id']}</code></div>
                <div>Session Status: <span style="background: var(--success-tint); color: var(--success); font-size: 0.76rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px;">Active</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Log out of StudyMate", key="settings_logout_btn", use_container_width=False):
        logout_callback()
        st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Academic Engine Health
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.4rem;">
                ⚡ Study Engine Status
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1rem;">
                Active status of StudyMate's learning and comprehension services.
            </p>
            <div style="font-size: 0.86rem; color: var(--text-secondary); line-height: 1.8;">
                <div>• <strong>Academic Knowledge Engine:</strong> Active & Connected</div>
                <div>• <strong>Comprehension Mode:</strong> High-Precision Fact Verification</div>
                <div>• <strong>Citation Grounding:</strong> Strict Textbook Alignment Enabled</div>
                <div>• <strong>Data Storage & Privacy:</strong> Encrypted & Isolated to Your Account</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
