"""Command-line interface for ingestion and lightweight retrieval evaluation."""
import argparse
import json
from pathlib import Path
from .clinical_rag.pipeline import ingest_directory, ask
from .clinical_rag.vector_store import VectorStore
from .clinical_rag.config import PROJECT_ROOT


def main():
    parser = argparse.ArgumentParser(description="Clinical Protocol RAG CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Index PDFs from dataset/pdfs")
    ingest.add_argument("--reset", action="store_true", help="Delete and rebuild the collection")
    sub.add_parser("evaluate", help="Run the local retrieval benchmark")
    query = sub.add_parser("ask", help="Ask a question from the terminal")
    query.add_argument("question")
    args = parser.parse_args()

    if args.command == "ingest":
        print(json.dumps(ingest_directory(reset=args.reset), indent=2))
    elif args.command == "evaluate":
        from evaluation.evaluate_retrieval import run_evaluation
        print(json.dumps(run_evaluation(), indent=2))
    elif args.command == "ask":
        result = ask(args.question)
        print(result["answer"])
        for item in result["evidence"]:
            meta = item["metadata"]
            print(f"\n[{meta.get('source')} | PDF p. {meta.get('page')} | distance={item['distance']:.3f}]")


if __name__ == "__main__":
    main()
