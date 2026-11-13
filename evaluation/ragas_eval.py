"""Optional RAGAS evaluation using a local Ollama judge.

RAGAS interfaces evolve. This adapter targets the RAGAS 0.2+ API. If the
installed release changes its interface, follow its official migration guide.
"""
import json
from pathlib import Path

from datasets import Dataset
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

from src.clinical_rag.pipeline import ask
from src.clinical_rag.config import settings

ROOT = Path(__file__).resolve().parents[1]


def main():
    pairs = json.loads((ROOT / "evaluation" / "qa_pairs.json").read_text(encoding="utf-8"))
    questions, answers, contexts, references = [], [], [], []
    for pair in pairs:
        result = ask(pair["question"])
        questions.append(pair["question"])
        answers.append(result["answer"])
        contexts.append([item["text"] for item in result["evidence"]])
        references.append(" ".join(pair["reference_keywords"]))

    data = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": references,
    })
    judge = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0)
    embeddings = OllamaEmbeddings(model=settings.ollama_model, base_url=settings.ollama_base_url)
    result = evaluate(
        data,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=judge,
        embeddings=embeddings,
    )
    output = result.to_pandas()
    output_path = ROOT / "evaluation" / "ragas_results.csv"
    output.to_csv(output_path, index=False)
    print(output.to_string(index=False))
    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
