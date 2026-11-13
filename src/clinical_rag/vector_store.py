"""ChromaDB persistence and local embedding generation."""
from pathlib import Path
from typing import Iterable
import chromadb
from sentence_transformers import SentenceTransformer
from .config import settings
from .ingestion import DocumentChunk


class VectorStore:
    def __init__(self, path: Path | None = None, collection_name: str | None = None):
        self.path = path or settings.chroma_path
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collection = self.client.get_or_create_collection(
            name=collection_name or settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.model = SentenceTransformer(settings.embedding_model)

    def reset(self) -> None:
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: Iterable[DocumentChunk], batch_size: int = 64) -> int:
        chunks = list(chunks)
        total = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            texts = [item.text for item in batch]
            embeddings = self.model.encode(texts, normalize_embeddings=True).tolist()
            self.collection.upsert(
                ids=[item.chunk_id for item in batch],
                documents=texts,
                metadatas=[item.metadata for item in batch],
                embeddings=embeddings,
            )
            total += len(batch)
        return total

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        if self.collection.count() == 0:
            return []
        vector = self.model.encode([question], normalize_embeddings=True).tolist()
        result = self.collection.query(
            query_embeddings=vector,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        rows = []
        for i, document in enumerate(result["documents"][0]):
            rows.append({
                "text": document,
                "metadata": result["metadatas"][0][i],
                "distance": float(result["distances"][0][i]),
                "id": result["ids"][0][i],
            })
        return rows
