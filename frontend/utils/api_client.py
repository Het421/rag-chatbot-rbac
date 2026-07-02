import os
import httpx
import streamlit as st

# Uses environment variable in production, falls back to localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 60.0


def get_auth_headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

# ... rest of the file stays the same}


# ─────────────────────────────────
# Auth
# ─────────────────────────────────

def login(employee_id: str, password: str) -> dict:
    """POST /auth/login"""
    response = httpx.post(
        f"{API_BASE_URL}/auth/login",
        json={"employee_id": employee_id, "password": password},
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def get_me() -> dict:
    """GET /auth/me — verify current token"""
    response = httpx.get(
        f"{API_BASE_URL}/auth/me",
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────
# Conversations
# ─────────────────────────────────

def create_conversation(title: str = "New Conversation") -> dict:
    """POST /chat/conversations"""
    response = httpx.post(
        f"{API_BASE_URL}/chat/conversations",
        json={"title": title},
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def list_conversations() -> list:
    """GET /chat/conversations"""
    response = httpx.get(
        f"{API_BASE_URL}/chat/conversations",
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def rename_conversation(conversation_id: str, title: str) -> dict:
    """PATCH /chat/conversations/{id}"""
    response = httpx.patch(
        f"{API_BASE_URL}/chat/conversations/{conversation_id}",
        json={"title": title},
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def delete_conversation(conversation_id: str) -> dict:
    """DELETE /chat/conversations/{id}"""
    response = httpx.delete(
        f"{API_BASE_URL}/chat/conversations/{conversation_id}",
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def get_messages(conversation_id: str) -> list:
    """GET /chat/conversations/{id}/messages"""
    response = httpx.get(
        f"{API_BASE_URL}/chat/conversations/{conversation_id}/messages",
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────
# RAG Chat
# ─────────────────────────────────

def send_message(conversation_id: str, message: str) -> dict:
    """POST /rag/chat"""
    response = httpx.post(
        f"{API_BASE_URL}/rag/chat",
        json={
            "conversation_id": conversation_id,
            "message": message
        },
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────
# Documents (Admin)
# ─────────────────────────────────

def upload_document(file_bytes: bytes, filename: str, access_level: str) -> dict:
    """POST /documents/upload"""
    response = httpx.post(
        f"{API_BASE_URL}/documents/upload",
        files={"file": (filename, file_bytes, "application/pdf")},
        data={"access_level": access_level},
        headers=get_auth_headers(),
        timeout=120.0  # uploading + ingesting can take longer
    )
    response.raise_for_status()
    return response.json()


def list_documents() -> list:
    """GET /documents/list"""
    response = httpx.get(
        f"{API_BASE_URL}/documents/list",
        headers=get_auth_headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()