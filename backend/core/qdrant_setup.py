from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from config import settings


def setup_qdrant():
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    collection_name = settings.QDRANT_COLLECTION_NAME

    # Check if collection already exists
    existing = client.get_collections()
    existing_names = [c.name for c in existing.collections]

    if collection_name not in existing_names:
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{collection_name}' created successfully!")
    else:
        print(f"Collection '{collection_name}' already exists — skipping creation.")

    # Create payload index on access_level field
    # This is required for filtering by access_level in Qdrant
    client.create_payload_index(
        collection_name=collection_name,
        field_name="access_level",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("Payload index on 'access_level' created successfully!")


if __name__ == "__main__":
    setup_qdrant()