import os
import shutil
from sqlalchemy.orm import Session

from documents.models import Document
from documents.ingestion import process_pdf
from documents.embeddings import get_embeddings_batch
from documents.qdrant_store import store_chunks_in_qdrant
from config import settings


def save_pdf_to_disk(file, filename: str) -> str:
    """
    Saves the uploaded file to disk.
    Returns the full file path where it was saved.
    """
    os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.PDF_STORAGE_PATH, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    return file_path


def ingest_document(
    filename: str,
    file_path: str,
    access_level: str,
    uploaded_by_id: str,
    db: Session
) -> dict:
    """
    Full ingestion pipeline:
    1. Save metadata to PostgreSQL
    2. Parse + chunk PDF
    3. Generate embeddings
    4. Store in Qdrant
    """

    # Step 1: Save document metadata to PostgreSQL
    document = Document(
        filename=filename,
        file_path=file_path,
        access_level=access_level,
        uploaded_by=uploaded_by_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    document_id = str(document.id)

    try:
        # Step 2: Parse and chunk the PDF
        chunks = process_pdf(file_path)

        if not chunks:
            db.delete(document)
            db.commit()
            raise ValueError("No text could be extracted from this PDF.")

        # Step 3: Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = get_embeddings_batch(texts)

        # Step 4: Store chunks + embeddings in Qdrant
        chunks_stored = store_chunks_in_qdrant(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=filename,
            access_level=access_level
        )

    except Exception as e:
        # If anything fails after saving to PostgreSQL, clean up
        db.delete(document)
        db.commit()
        raise e

    return {
        "document_id": document_id,
        "filename": filename,
        "access_level": access_level,
        "chunks_created": chunks_stored
    }