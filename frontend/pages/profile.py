import streamlit as st


def profile_page():
    """User profile page."""

    st.title("👤 My Profile")
    st.caption("Your account information.")

    st.divider()

    # Profile info cards
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Account Details")
        st.write(f"**Full Name:** {st.session_state.get('full_name', 'N/A')}")
        st.write(f"**Employee ID:** {st.session_state.get('employee_id', 'N/A')}")
        st.write(f"**Role:** {st.session_state.get('role', 'N/A').capitalize()}")

    with col2:
        st.subheader("Access Level")
        role = st.session_state.get("role", "employee")
        if role == "admin":
            st.success("🔑 Admin — Full access to all documents and admin panel")
        else:
            st.info("👤 Employee — Access to company-wide documents")

    st.divider()

    # Default password notice
    st.subheader("🔒 Password")
    st.warning(
        "Your default password is your Employee ID. "
        "Password change functionality will be available in a future update."
    )

    st.divider()

    # Logout button
    if st.button("🚪 Logout", use_container_width=False):
        from utils.session import logout_user
        logout_user()
        st.rerun()