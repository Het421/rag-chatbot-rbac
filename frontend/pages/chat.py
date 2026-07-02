import streamlit as st
from utils.api_client import (
    create_conversation,
    list_conversations,
    delete_conversation,
    rename_conversation,
    get_messages,
    send_message
)


def render_sidebar():
    """Renders the conversation sidebar."""
    with st.sidebar:
        st.title("💬 Conversations")

        # New conversation button
        if st.button("➕ New Conversation", use_container_width=True):
            try:
                conv = create_conversation("New Conversation")
                st.session_state.active_conversation_id = conv["id"]
                st.session_state.active_conversation_title = conv["title"]
                st.session_state.messages = []
                st.rerun()
            except Exception as e:
                st.error(f"Error creating conversation: {e}")

        st.divider()

        # List existing conversations
        try:
            conversations = list_conversations()
        except Exception:
            st.error("Could not load conversations.")
            return

        if not conversations:
            st.caption("No conversations yet. Start a new one!")
            return

        for conv in conversations:
            conv_id = conv["id"]
            conv_title = conv["title"]
            is_active = conv_id == st.session_state.get("active_conversation_id")

            # Highlight active conversation
            if is_active:
                st.markdown(f"**▶ {conv_title}**")
            else:
                if st.button(conv_title, key=f"conv_{conv_id}", use_container_width=True):
                    load_conversation(conv_id, conv_title)
                    st.rerun()

            # Rename + Delete buttons for each conversation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️", key=f"rename_{conv_id}", help="Rename"):
                    st.session_state[f"renaming_{conv_id}"] = True
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{conv_id}", help="Delete"):
                    try:
                        delete_conversation(conv_id)
                        if conv_id == st.session_state.get("active_conversation_id"):
                            st.session_state.active_conversation_id = None
                            st.session_state.messages = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            # Rename input field
            if st.session_state.get(f"renaming_{conv_id}"):
                new_title = st.text_input(
                    "New name",
                    value=conv_title,
                    key=f"rename_input_{conv_id}"
                )
                if st.button("Save", key=f"save_rename_{conv_id}"):
                    try:
                        rename_conversation(conv_id, new_title)
                        st.session_state[f"renaming_{conv_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.divider()

        # Logout button at bottom of sidebar
        if st.button("🚪 Logout", use_container_width=True):
            from utils.session import logout_user
            logout_user()
            st.rerun()


def load_conversation(conv_id: str, conv_title: str):
    """Loads a conversation's messages into session state."""
    try:
        messages = get_messages(conv_id)
        st.session_state.active_conversation_id = conv_id
        st.session_state.active_conversation_title = conv_title
        st.session_state.messages = messages
    except Exception as e:
        st.error(f"Could not load conversation: {e}")


def render_messages():
    """Renders all messages in the active conversation."""
    messages = st.session_state.get("messages", [])

    if not messages:
        st.info("No messages yet. Ask a question below!")
        return

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        sources = msg.get("sources", [])

        with st.chat_message(role):
            st.markdown(content)

            # Show sources for assistant messages
            if role == "assistant" and sources:
                valid_sources = [
                    s for s in sources
                    if s.get("filename", "Unknown") != "Unknown"
                ]
                if valid_sources:
                    with st.expander("📄 Sources"):
                        for source in valid_sources:
                            st.caption(
                                f"📌 {source['filename']} — Page {source['page_number']}"
                            )


def chat_page():
    """Main chat page."""

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    if "active_conversation_title" not in st.session_state:
        st.session_state.active_conversation_title = None

    # Render sidebar
    render_sidebar()

    # Main chat area header
    active_title = st.session_state.get("active_conversation_title", "")
    if active_title:
        st.title(f"💬 {active_title}")
    else:
        st.title("💬 Company Chatbot")
        st.caption(f"Welcome, **{st.session_state.get('full_name', '')}** "
                   f"| Role: **{st.session_state.get('role', '')}**")

    # If no active conversation, prompt to start one
    if not st.session_state.get("active_conversation_id"):
        st.info("👈 Select a conversation from the sidebar or create a new one.")
        return

    # Render existing messages
    render_messages()

    # Chat input
    if prompt := st.chat_input("Ask a question about company documents..."):
        # Immediately show user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add to local session messages for immediate display
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "sources": None
        })

        # Call RAG endpoint
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    result = send_message(
                        conversation_id=st.session_state.active_conversation_id,
                        message=prompt
                    )

                    answer = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    # Show sources
                    valid_sources = [
                        s for s in sources
                        if s.get("filename", "Unknown") != "Unknown"
                    ]
                    if valid_sources:
                        with st.expander("📄 Sources"):
                            for source in valid_sources:
                                st.caption(
                                    f"📌 {source['filename']} "
                                    f"— Page {source['page_number']}"
                                )

                    # Add assistant response to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")