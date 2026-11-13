from pathlib import Path
import fitz
from src.clinical_rag.ingestion import extract_pdf_pages, build_chunks


def test_pdf_extraction_preserves_physical_page(tmp_path: Path):
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Clinical guideline sample text.")
    doc.save(path)
    doc.close()

    pages = extract_pdf_pages(path)
    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert "Clinical guideline" in pages[0]["text"]


def test_build_chunks_has_page_metadata(tmp_path: Path):
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Evidence based guideline content. " * 20)
    doc.save(path)
    doc.close()

    chunks = build_chunks(path, chunk_size=100, overlap=10)
    assert chunks
    assert all(chunk.metadata["page"] == 1 for chunk in chunks)
