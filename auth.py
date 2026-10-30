"""Authentication utilities for the Academic RAG Assistant.

Provides:
- Secure password hashing and verification using bcrypt
- Registration and login validation
- Session-based authentication helpers for Streamlit
"""

import re
from typing import Any, Dict, Optional, Tuple

import bcrypt
import streamlit as st

import database


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with a salt work factor of 12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def validate_registration_inputs(
    username: str, email: str, password: str
) -> Tuple[bool, Optional[str]]:
    """Validate user registration inputs."""
    username = (username or "").strip()
    email = (email or "").strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username may only contain letters, numbers, hyphens, and underscores."
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    return True, None


def register_user(
    username: str, email: str, password: str, db_path=None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Register a new user in the database."""
    is_valid, error_msg = validate_registration_inputs(username, email, password)
    if not is_valid:
        return None, error_msg

    # Check if username or email already exists
    existing_user = database.get_user_by_username_or_email(username, db_path=db_path)
    if existing_user:
        return None, "Username or email is already registered."

    existing_email = database.get_user_by_email(email, db_path=db_path)
    if existing_email:
        return None, "An account with this email already exists."

    pwd_hash = hash_password(password)
    try:
        user = database.create_user(
            username=username,
            email=email,
            password_hash=pwd_hash,
            db_path=db_path,
        )
        return user, None
    except Exception as exc:
        return None, f"Registration failed: {exc}"


def authenticate_user(
    identifier: str, password: str, db_path=None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Authenticate a user by username or email and password."""
    identifier_clean = (identifier or "").strip()
    if not identifier_clean or not password:
        return None, "Please enter both username/email and password."

    user = database.get_user_by_username_or_email(identifier_clean, db_path=db_path)
    if not user:
        return None, "Invalid username or password."

    if not verify_password(password, user["password_hash"]):
        return None, "Invalid username or password."

    return user, None


# ============================================================================
# Streamlit Session Helpers
# ============================================================================

def is_authenticated() -> bool:
    """Check if the current session has an authenticated user."""
    return bool(st.session_state.get("authenticated") and st.session_state.get("user"))


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user dictionary from session state."""
    return st.session_state.get("user")


def login_user(user: Dict[str, Any]) -> None:
    """Set session state for an authenticated user."""
    st.session_state.authenticated = True
    st.session_state.user = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }
    st.session_state.page = "home"
    st.session_state.current_conversation_id = None
    st.session_state.messages = []


def logout_user() -> None:
    """Clear session state and log out the user."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.uploaded_documents = {}
    st.session_state.page = "auth"
