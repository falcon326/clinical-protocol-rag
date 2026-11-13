import pytest
from src.clinical_rag.ingestion import chunk_text, normalize_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("   ") == []


def test_chunking_preserves_content():
    text = "alpha " * 100
    chunks = chunk_text(text, chunk_size=80, overlap=10)
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert "alpha" in "".join(chunks)


def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=10, overlap=10)


def test_normalize_text():
    assert normalize_text("a   b\n\n\nc") == "a b\n\nc"
