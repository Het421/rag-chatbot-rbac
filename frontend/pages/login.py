import streamlit as st
import httpx

from utils.session import login_user
from utils.api_client import login


def login_page():
    st.title("🔐 Company Chatbot — Login")
    st.caption("Enter your Employee ID. Your default password is your Employee ID.")

    with st.form("login_form"):
        employee_id = st.text_input("Employee ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not employee_id or not password:
            st.error("Please enter both Employee ID and Password.")
            return

        try:
            result = login(employee_id, password)
            login_user(
                token=result["access_token"],
                role=result["role"],
                full_name=result["full_name"],
                employee_id=employee_id
            )
            st.success(f"Welcome, {result['full_name']}!")
            st.rerun()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                st.error("Invalid Employee ID or Password.")
            elif e.response.status_code == 403:
                st.error("Your account has been deactivated. Contact admin.")
            else:
                st.error("Something went wrong. Please try again.")

        except httpx.ConnectError:
            st.error("Cannot connect to the server. Is the backend running?")