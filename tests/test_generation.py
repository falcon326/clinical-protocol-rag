from src.clinical_rag.generation import extractive_fallback


def test_fallback_abstains_without_evidence():
    assert "not provide enough evidence" in extractive_fallback([])


def test_fallback_includes_source_and_page():
    evidence = [{
        "text": "A guideline passage.",
        "metadata": {"title": "Test guideline", "page": 7, "source": "test.pdf"}
    }]
    result = extractive_fallback(evidence)
    assert "Test guideline" in result
    assert "page 7" in result
    assert "A guideline passage." in result
