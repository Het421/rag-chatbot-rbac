import streamlit as st
from utils.api_client import upload_document, list_documents


def admin_page():
    """Admin panel for PDF management."""

    # Double check role on frontend too
    if st.session_state.get("role") != "admin":
        st.error("⛔ Access Denied. This page is for admins only.")
        return

    st.title("🛠️ Admin Panel")
    st.caption(f"Logged in as **{st.session_state.get('full_name')}** (Admin)")

    tab1, tab2 = st.tabs(["📤 Upload PDF", "📋 Manage Documents"])

    # ─────────────────────────────────
    # Tab 1 — Upload PDF
    # ─────────────────────────────────
    with tab1:
        st.subheader("Upload a New PDF")
        st.caption("Uploaded PDFs will be parsed, chunked, and embedded automatically.")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Only PDF files are supported."
        )

        access_level = st.radio(
            "Who can access this document?",
            options=["all_employees", "admin_only"],
            format_func=lambda x: "All Employees" if x == "all_employees" else "Admin Only",
            horizontal=True
        )

        if uploaded_file is not None:
            st.info(f"Selected: **{uploaded_file.name}** "
                    f"({round(uploaded_file.size / 1024, 1)} KB)")

            if st.button("🚀 Upload & Ingest", use_container_width=True):
                with st.spinner(
                    f"Uploading and ingesting '{uploaded_file.name}'... "
                    "This may take a moment."
                ):
                    try:
                        result = upload_document(
                            file_bytes=uploaded_file.getvalue(),
                            filename=uploaded_file.name,
                            access_level=access_level
                        )
                        st.success(f"✅ {result['message']}")
                        st.json({
                            "Document ID": str(result["id"]),
                            "Filename": result["filename"],
                            "Access Level": result["access_level"],
                            "Chunks Created": result["chunks_created"]
                        })
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")

    # ─────────────────────────────────
    # Tab 2 — Manage Documents
    # ─────────────────────────────────
    with tab2:
        st.subheader("All Uploaded Documents")

        if st.button("🔄 Refresh", use_container_width=False):
            st.rerun()

        try:
            documents = list_documents()

            if not documents:
                st.info("No documents uploaded yet.")
                return

            # Summary metrics
            total = len(documents)
            admin_only = sum(
                1 for d in documents if d["access_level"] == "admin_only"
            )
            all_emp = total - admin_only

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Documents", total)
            col2.metric("All Employees", all_emp)
            col3.metric("Admin Only", admin_only)

            st.divider()

            # Document list
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Document ID:** {doc['id']}")
                        st.write(f"**Uploaded:** {doc['created_at'][:10]}")
                    with col2:
                        if doc["access_level"] == "all_employees":
                            st.success("🌐 All Employees")
                        else:
                            st.warning("🔒 Admin Only")

        except Exception as e:
            st.error(f"Could not load documents: {str(e)}")