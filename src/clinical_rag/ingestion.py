"""PDF extraction and deterministic, page-aware text chunking."""
from dataclasses import dataclass
from pathlib import Path
import re
import fitz


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    """Return one record per non-empty physical PDF page (1-based page index)."""
    records = []
    with fitz.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            text = normalize_text(page.get_text("text"))
            if text:
                records.append({
                    "text": text,
                    "page": page_index,
                    "source": pdf_path.name,
                    "title": pdf_path.stem.replace("_", " ").strip(),
                })
    return records


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """Split text into character-bounded chunks with overlap and no empty chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")
    text = normalize_text(text)
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
            if boundary > start + int(chunk_size * 0.6):
                end = boundary
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        next_start = max(start + 1, end - overlap)
        start = next_start
    return chunks


def build_chunks(pdf_path: Path, chunk_size: int, overlap: int) -> list[DocumentChunk]:
    chunks = []
    for page_record in extract_pdf_pages(pdf_path):
        for index, text in enumerate(chunk_text(page_record["text"], chunk_size, overlap)):
            chunk_id = f"{pdf_path.stem}-p{page_record['page']}-c{index}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                metadata={
                    "source": page_record["source"],
                    "title": page_record["title"],
                    "page": page_record["page"],
                    "chunk_index": index,
                },
            ))
    return chunks
