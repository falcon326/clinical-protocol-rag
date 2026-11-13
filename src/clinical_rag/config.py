"""Central configuration loaded from environment variables."""
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    chroma_path: Path = PROJECT_ROOT / os.getenv("CHROMA_PATH", "storage/chroma")
    collection_name: str = os.getenv("COLLECTION_NAME", "clinical_guidelines")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    min_relevance_distance: float = float(os.getenv("MIN_RELEVANCE_DISTANCE", "1.25"))
    use_llm: bool = os.getenv("USE_LLM", "true").lower() in {"1", "true", "yes"}
    dataset_dir: Path = PROJECT_ROOT / "dataset" / "pdfs"


settings = Settings()
