from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import settings

# Initialize embeddings model
embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def get_all_chunks_as_docs(user_role: str) -> list[Document]:
    """
    Fetches all accessible chunks from Qdrant based on user role.
    Returns them as LangChain Document objects for BM25.
    """
    if user_role == "admin":
        qdrant_filter = None
    else:
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="access_level",
                    match=MatchValue(value="all_employees")
                )
            ]
        )

    all_chunks, _ = qdrant_client.scroll(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        scroll_filter=qdrant_filter,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    return [
        Document(
            page_content=chunk.payload["chunk_text"],
            metadata={
                "filename": chunk.payload["filename"],
                "page_number": chunk.payload["page_number"],
                "access_level": chunk.payload["access_level"],
                "document_id": chunk.payload["document_id"],
            }
        )
        for chunk in all_chunks
    ]


def hybrid_search(
    query: str,
    user_role: str,
    top_k: int = 5
) -> list[dict]:
    """
    Performs hybrid search combining BM25 + Qdrant semantic search.
    Merges and deduplicates results manually.
    """

    # Step 1: Get all accessible docs for BM25
    all_docs = get_all_chunks_as_docs(user_role)

    if not all_docs:
        return []

    # Step 2: BM25 retrieval
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = top_k
    bm25_results = bm25_retriever.invoke(query)

    # Step 3: Qdrant semantic retrieval with RBAC filter
    if user_role == "admin":
        qdrant_filter = None
    else:
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="access_level",
                    match=MatchValue(value="all_employees")
                )
            ]
        )

    qdrant_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embedding=embeddings,
    )

    semantic_retriever = qdrant_store.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": qdrant_filter
        }
    )
    semantic_results = semantic_retriever.invoke(query)

    # Step 4: Merge + deduplicate by page_content
    seen_texts = set()
    merged = []

    # Semantic results get priority (added first)
    for doc in semantic_results:
        if doc.page_content not in seen_texts:
            seen_texts.add(doc.page_content)
            merged.append(doc)

    # BM25 results fill in unique additions
    for doc in bm25_results:
        if doc.page_content not in seen_texts:
            seen_texts.add(doc.page_content)
            merged.append(doc)

    # Step 5: Format and return top_k
    formatted = []
    for doc in merged[:top_k]:
        formatted.append({
            "chunk_text": doc.page_content,
            "filename": doc.metadata.get("filename", "Unknown"),
            "page_number": doc.metadata.get("page_number", 0),
            "access_level": doc.metadata.get("access_level", ""),
        })

    return formatted