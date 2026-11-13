"""Small source-retrieval benchmark; no external LLM/API calls."""
import json
from pathlib import Path
from src.clinical_rag.pipeline import ask

ROOT = Path(__file__).resolve().parents[1]


def run_evaluation() -> dict:
    dataset = json.loads((ROOT / "evaluation" / "qa_pairs.json").read_text(encoding="utf-8"))
    hits, reciprocal_ranks, details = 0, [], []
    for item in dataset:
        result = ask(item["question"])
        source_ids = [row["metadata"].get("source", "") for row in result["evidence"]]
        expected = "who_mhgap_guideline_2023.pdf"
        rank = next((i + 1 for i, source in enumerate(source_ids) if source == expected), None)
        hits += int(rank is not None)
        reciprocal_ranks.append(1 / rank if rank else 0.0)
        details.append({"question": item["question"], "expected_source_rank": rank, "retrieved_sources": source_ids})
    count = len(dataset)
    return {
        "benchmark_size": count,
        "hit_rate_at_k": hits / count if count else 0.0,
        "mrr_at_k": sum(reciprocal_ranks) / count if count else 0.0,
        "details": details,
        "warning": "Starter retrieval benchmark only; not a clinical validation."
    }


if __name__ == "__main__":
    print(json.dumps(run_evaluation(), indent=2))
