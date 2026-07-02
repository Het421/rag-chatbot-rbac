from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from core.dependencies import get_current_user
from auth.models import User
from chat.models import Conversation, Message
from chat.schemas import ChatRequest, ChatResponse
from rag.query_rewriter import rewrite_query
from rag.hybrid_search import hybrid_search
from rag.chain import generate_answer

router = APIRouter(prefix="/rag", tags=["RAG Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Step 1: Verify conversation belongs to this user
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Step 2: Load conversation history from PostgreSQL
    history_messages = db.query(Message).filter(
        Message.conversation_id == request.conversation_id
    ).order_by(Message.created_at.asc()).all()

    # Format history for RAG pipeline
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    # Step 3: Rewrite query using Groq
    rewritten_query = rewrite_query(
        original_query=request.message,
        conversation_history=conversation_history
    )

    # Step 4: Hybrid search with RBAC
    chunks = hybrid_search(
        query=rewritten_query,
        user_role=current_user.role,
        top_k=5
    )

    # Step 5: Generate answer using Groq LLM
    result = generate_answer(
        question=request.message,
        chunks=chunks,
        conversation_history=conversation_history
    )

    # Step 6: Save user message to PostgreSQL
    user_message = Message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        sources=None
    )
    db.add(user_message)

    # Step 7: Save assistant response to PostgreSQL
    assistant_message = Message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"]
    )
    db.add(assistant_message)

    # Step 8: Update conversation's updated_at timestamp
    from datetime import datetime
    conversation.updated_at = datetime.utcnow()

    db.commit()

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        conversation_id=request.conversation_id
    )