"""Public landing page introducing StudyMate."""

import streamlit as st


def render_landing_page():
    """Render the public product showcase page."""
    # Top Minimal Nav
    _nav_l, _nav_r = st.columns([6, 3])
    with _nav_l:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0;">
                <span style="font-size: 1.5rem;">📚</span>
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.3rem; font-weight: 800; color: var(--text-primary);">StudyMate</span>
                <span style="background: var(--badge-bg); color: var(--badge-text); font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 6px; text-transform: uppercase;">Academic AI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with _nav_r:
        _btn_sign, _btn_reg = st.columns(2)
        with _btn_sign:
            if st.button("Sign In", key="landing_top_signin", use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.session_state.page = "auth"
                st.rerun()
        with _btn_reg:
            if st.button("Get Started", key="landing_top_signup", type="primary", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.session_state.page = "auth"
                st.rerun()

    st.markdown("<div style='margin-top: 2.2rem;'></div>", unsafe_allow_html=True)

    # Hero Banner
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 3.5rem 1.5rem 2.5rem;
            background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-subtle) 100%);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            box-shadow: var(--shadow-md);
            margin-bottom: 2.5rem;
        ">
            <div style="
                display: inline-block;
                background: var(--badge-bg);
                color: var(--badge-text);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                padding: 0.35rem 0.85rem;
                border-radius: 30px;
                margin-bottom: 1.2rem;
            ">
                ✦ Grounded Academic Intelligence
            </div>
            <h1 style="
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 3.2rem;
                font-weight: 800;
                line-height: 1.15;
                color: var(--text-primary);
                margin: 0 0 1rem;
                letter-spacing: -0.03em;
            ">
                Learn smarter.<br>Study with your own material.
            </h1>
            <p style="
                font-size: 1.18rem;
                color: var(--text-secondary);
                max-width: 640px;
                margin: 0 auto 2rem;
                line-height: 1.65;
            ">
                StudyMate turns your academic textbooks, lecture slides, and notes
                into an interactive study assistant with verifiable source citations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _c_l, _c_m, _c_r = st.columns([1.5, 2.2, 1.5])
    with _c_m:
        _act1, _act2 = st.columns(2)
        with _act1:
            if st.button("🚀 Get Started", key="hero_cta_start", type="primary", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.session_state.page = "auth"
                st.rerun()
        with _act2:
            if st.button("Sign In", key="hero_cta_signin", use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.session_state.page = "auth"
                st.rerun()

    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)

    # 3-Pillar Value Proposition
    col1, col2, col3 = st.columns(3, gap="medium")
    pillars = [
        ("📄", "Upload", "Add your study materials", "Drop in textbooks, syllabus handouts, or lecture slides. StudyMate organizes your notes for instant, accurate learning."),
        ("🔎", "Ask Naturally", "Ask any question", "Query concepts, formulas, and summaries. StudyMate searches precisely through your uploaded materials."),
        ("💡", "Learn & Verify", "Fact-checked answers", "Receive clear academic explanations with exact page numbers and quotes from your textbooks."),
    ]
    for col, (icon, step, title, text) in zip([col1, col2, col3], pillars):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: var(--bg-surface);
                    border: 1px solid var(--border-color);
                    border-radius: 16px;
                    padding: 1.6rem 1.4rem;
                    height: 100%;
                    box-shadow: var(--shadow-sm);
                    transition: transform 0.2s ease;
                ">
                    <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">{icon}</div>
                    <div style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand-accent);">{step}</div>
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 0.2rem 0 0.6rem;">{title}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)

    # Trust Banner
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 2.2rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
        ">
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem;">
                Built for students who want answers from THEIR material.
            </div>
            <p style="color: var(--text-secondary); font-size: 0.95rem; max-width: 600px; margin: 0 auto;">
                Zero generic web search hallucinations. Every generated response is strictly anchored
                in the passages retrieved from your uploaded academic documents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
