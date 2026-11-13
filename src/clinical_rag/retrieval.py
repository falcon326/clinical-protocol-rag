"""Evidence retrieval and relevance filtering."""
from .vector_store import VectorStore
from .config import settings


def retrieve_evidence(question: str, store: VectorStore, top_k: int | None = None) -> list[dict]:
    if not question or not question.strip():
        return []
    results = store.query(question.strip(), top_k or settings.top_k)
    cutoff = settings.min_relevance_distance
    return [row for row in results if row["distance"] <= cutoff]
