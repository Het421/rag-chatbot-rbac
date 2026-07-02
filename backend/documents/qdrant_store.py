import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from config import settings

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def store_chunks_in_qdrant(
    chunks: list[dict],
    embeddings: list[list[float]],
    document_id: str,
    filename: str,
    access_level: str
):
    """
    Stores chunks + their embeddings into Qdrant, along with metadata
    needed for RBAC filtering and source citation later.
    """
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": document_id,
                "filename": filename,
                "access_level": access_level,
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["text"],
            }
        )
        points.append(point)

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points
    )

    return len(points)