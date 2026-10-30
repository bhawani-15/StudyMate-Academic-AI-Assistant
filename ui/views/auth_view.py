"""Authentication view for StudyMate (Sign In and Create Account)."""

import streamlit as st
import auth
import database


def render_auth_view(sync_documents_callback):
    """Render the authentication screen with Sign In and Create Account tabs."""
    _col_l, _col_mid, _col_r = st.columns([1, 1.8, 1])

    with _col_mid:
        # Back to landing link
        if st.button("← Back to Welcome Page", key="auth_back_landing"):
            st.session_state.page = "landing"
            st.rerun()

        st.markdown(
            """
            <div style="
                background: var(--bg-surface);
                border: 1px solid var(--border-color);
                border-radius: 18px;
                padding: 2.2rem 2.4rem 1.6rem;
                box-shadow: var(--shadow-lg);
                margin-top: 1rem;
            ">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.2rem;">📚</div>
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--text-primary); margin: 0;">StudyMate</div>
                    <div style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem;">Your Academic AI Study Assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        initial_tab = 1 if st.session_state.get("auth_tab") == "signup" else 0
        tab_signin, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_signin:
            st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
            with st.form("signin_form", clear_on_submit=False):
                identifier = st.text_input(
                    "Username or Email",
                    placeholder="e.g. student or student@college.edu",
                    key="signin_identifier",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="signin_password",
                )
                submit_signin = st.form_submit_button("Sign In to StudyMate", type="primary", use_container_width=True)

                if submit_signin:
                    user, err = auth.authenticate_user(identifier, password)
                    if err:
                        st.error(err)
                    else:
                        auth.login_user(user)
                        sync_documents_callback(user["id"])
                        st.session_state.page = "dashboard"
                        st.rerun()

            # Friction-free Demo Quick Login
            st.markdown("<div style='text-align: center; margin: 1.2rem 0 0.4rem;'><small style='color: var(--text-light);'>Fast evaluation access:</small></div>", unsafe_allow_html=True)
            if st.button("⚡ Continue with Demo Account", key="demo_student_btn", use_container_width=True):
                demo_user = database.get_user_by_username_or_email("student")
                if not demo_user:
                    demo_user, _ = auth.register_user("student", "student@university.edu", "password123")
                if demo_user:
                    auth.login_user(demo_user)
                    sync_documents_callback(demo_user["id"])
                    st.session_state.page = "dashboard"
                    st.rerun()

        with tab_signup:
            st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=False):
                reg_username = st.text_input("Username", placeholder="e.g. bhawani", key="signup_username")
                reg_email = st.text_input("Email", placeholder="e.g. bhawani@college.edu", key="signup_email")
                reg_password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="signup_password")
                submit_signup = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if submit_signup:
                    user, err = auth.register_user(reg_username, reg_email, reg_password)
                    if err:
                        st.error(err)
                    else:
                        auth.login_user(user)
                        sync_documents_callback(user["id"])
                        st.session_state.page = "dashboard"
                        st.rerun()
