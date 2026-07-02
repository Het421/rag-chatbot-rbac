from sentence_transformers import SentenceTransformer
from config import settings

# Load the model once when this module is first imported (not on every call)
_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def get_embedding(text: str) -> list[float]:
    """Converts a single piece of text into a 384-dim vector."""
    embedding = _model.encode(text)
    return embedding.tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Converts multiple texts into vectors at once — much faster than one at a time."""
    embeddings = _model.encode(texts)
    return embeddings.tolist()