from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Literal


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    access_level: Literal["admin_only", "all_employees"]
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    access_level: str
    chunks_created: int
    message: str