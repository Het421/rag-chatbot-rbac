import streamlit as st


def init_session():
    """Initialize session state variables if they don't exist yet."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "full_name" not in st.session_state:
        st.session_state.full_name = None
    if "employee_id" not in st.session_state:
        st.session_state.employee_id = None


def login_user(token: str, role: str, full_name: str, employee_id: str):
    """Store user session after successful login."""
    st.session_state.token = token
    st.session_state.role = role
    st.session_state.full_name = full_name
    st.session_state.employee_id = employee_id


def logout_user():
    """Clear session — used on logout."""
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.session_state.employee_id = None


def is_logged_in() -> bool:
    return st.session_state.get("token") is not None