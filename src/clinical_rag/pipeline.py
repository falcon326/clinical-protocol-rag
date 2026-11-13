"""End-to-end ingestion and question-answering orchestration."""
from pathlib import Path
from .config import settings
from .ingestion import build_chunks
from .vector_store import VectorStore
from .retrieval import retrieve_evidence
from .generation import generate_answer


def ingest_directory(directory: Path | None = None, reset: bool = False) -> dict:
    directory = directory or settings.dataset_dir
    pdfs = sorted(directory.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(
            f"No PDF files found in {directory}. Run: python dataset/download_dataset.py"
        )
    store = VectorStore()
    if reset:
        store.reset()
    total = 0
    per_file = {}
    for pdf in pdfs:
        chunks = build_chunks(pdf, settings.chunk_size, settings.chunk_overlap)
        count = store.add_chunks(chunks)
        per_file[pdf.name] = count
        total += count
    return {"pdf_count": len(pdfs), "chunk_count": total, "files": per_file}


def ask(question: str, store: VectorStore | None = None) -> dict:
    store = store or VectorStore()
    evidence = retrieve_evidence(question, store)
    answer, mode = generate_answer(question, evidence)
    return {"question": question, "answer": answer, "mode": mode, "evidence": evidence}
