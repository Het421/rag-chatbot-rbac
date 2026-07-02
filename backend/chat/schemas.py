from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: Optional[list[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    conversation_id: UUID
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    conversation_id: UUID