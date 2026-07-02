from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Literal

from database import get_db
from core.dependencies import require_admin, get_current_user
from auth.models import User
from documents.models import Document
from documents.schemas import DocumentUploadResponse, DocumentResponse
from documents.service import save_pdf_to_disk, ingest_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    access_level: Literal["admin_only", "all_employees"] = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Only accept PDF files
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save to disk
    file_path = save_pdf_to_disk(file.file, file.filename)

    # Run full ingestion pipeline
    result = ingest_document(
        filename=file.filename,
        file_path=file_path,
        access_level=access_level,
        uploaded_by_id=str(current_user.id),
        db=db
    )

    return DocumentUploadResponse(
        id=result["document_id"],
        filename=result["filename"],
        access_level=result["access_level"],
        chunks_created=result["chunks_created"],
        message=f"Successfully ingested '{file.filename}' into {result['chunks_created']} chunks."
    )


@router.get("/list", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admins see all documents.
    Employees see only 'all_employees' documents.
    """
    if current_user.role == "admin":
        documents = db.query(Document).all()
    else:
        documents = db.query(Document).filter(
            Document.access_level == "all_employees"
        ).all()

    return documents