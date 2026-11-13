"""Grounded answer generation via Ollama, with a safe extractive fallback."""
import requests
from .config import settings

SYSTEM_PROMPT = """You are a careful clinical-literature research assistant.
Answer only from the supplied evidence. Do not use outside knowledge.
Every factual statement must carry an inline citation in the form [Source: filename, PDF p. N].
If the evidence does not contain the answer, say: "The available documents do not provide enough evidence to answer this question."
Do not diagnose, prescribe, recommend patient-specific treatment, or infer missing clinical details.
Distinguish guideline recommendations from background explanations. Mention uncertainty and conflicting evidence.
This is an educational literature assistant, not a clinical decision-support tool."""


def format_context(evidence: list[dict]) -> str:
    blocks = []
    for item in evidence:
        meta = item["metadata"]
        blocks.append(
            f"[Source: {meta.get('source', 'unknown')}, PDF p. {meta.get('page', '?')}]\n"
            f"{item['text']}"
        )
    return "\n\n---\n\n".join(blocks)


def extractive_fallback(evidence: list[dict]) -> str:
    if not evidence:
        return "The available documents do not provide enough evidence to answer this question."
    lines = [
        "The local language model is unavailable. The following are retrieved source excerpts, "
        "not a synthesized clinical answer:"
    ]
    for item in evidence[:3]:
        meta = item["metadata"]
        excerpt = item["text"].strip()
        if len(excerpt) > 850:
            excerpt = excerpt[:850].rsplit(" ", 1)[0] + "…"
        lines.append(
            f"\n\n**{meta.get('title', meta.get('source', 'Source'))} — PDF page "
            f"{meta.get('page', 'unknown')}**\n{excerpt}"
        )
    return "\n".join(lines)


def generate_answer(question: str, evidence: list[dict]) -> tuple[str, str]:
    if not evidence:
        return (
            "The available documents do not provide enough evidence to answer this question. "
            "Try rephrasing the question or adding a relevant guideline.",
            "abstained",
        )
    if not settings.use_llm:
        return extractive_fallback(evidence), "extractive_fallback"

    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nRetrieved evidence:\n{format_context(evidence)}",
            },
        ],
        "options": {"temperature": 0.1},
    }
    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
            timeout=(10, 180),
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()
        if not answer:
            raise ValueError("Ollama returned an empty response.")
        return answer, "ollama"
    except (requests.RequestException, KeyError, ValueError) as exc:
        return (
            extractive_fallback(evidence)
            + f"\n\n*Generation service unavailable ({type(exc).__name__}); showing retrieved evidence instead.*",
            "extractive_fallback",
        )
