import streamlit as st
from utils.session import init_session, is_logged_in
from pages.login import login_page
from pages.chat import chat_page
from pages.admin import admin_page
from pages.profile import profile_page

st.set_page_config(
    page_title="Company RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

init_session()

if not is_logged_in():
    login_page()
else:
    with st.sidebar:
        st.markdown(f"👋 **{st.session_state.get('full_name', '')}**")
        st.caption(f"Role: {st.session_state.get('role', '').capitalize()}")
        st.divider()

        # Build navigation options based on role
        nav_options = ["💬 Chat", "👤 Profile"]
        if st.session_state.get("role") == "admin":
            nav_options.append("🛠️ Admin Panel")

        page = st.radio(
            "Navigation",
            options=nav_options,
            label_visibility="collapsed"
        )

    if page == "💬 Chat":
        chat_page()
    elif page == "👤 Profile":
        profile_page()
    elif page == "🛠️ Admin Panel":
        admin_page()