# Clinical Protocol & Medical Literature Assistant
### An End-to-End, Source-Grounded Retrieval-Augmented Generation (RAG) System

A local-first research assistant that retrieves evidence from clinical guideline PDFs and generates answers with document-level and page-level citations.

> **Important medical disclaimer:** This is an educational information-retrieval and literature-assistance prototype. It is not a medical device and must not be used to diagnose, treat, triage, or make patient-care decisions. Always consult qualified healthcare professionals and current authoritative guidance.

## Project highlights

- PDF ingestion with page-level provenance using PyMuPDF.
- Configurable text chunking with overlap.
- Local sentence-transformer embeddings (`all-MiniLM-L6-v2`).
- Persistent ChromaDB vector store.
- Semantic retrieval with source and page metadata.
- Optional local LLM generation through Ollama (no paid API required).
- Conservative extractive fallback when the LLM is unavailable.
- Streamlit interface with visible evidence snippets.
- Automated tests and an evaluation workflow, including optional RAGAS integration.

## Architecture

```text
WHO guideline PDFs
       |
       v
PDF ingestion (PyMuPDF; preserve page metadata)
       |
       v
Text cleaning + chunking + overlap
       |
       v
Sentence Transformers embeddings
       |
       v
ChromaDB (persistent vector database)
       |
User question -> semantic retrieval (top-k)
       |
       v
Retrieved evidence + strict generation prompt
       |
       +---- Ollama local LLM (optional)
       |
       v
Answer + source title + PDF page numbers + evidence
       |
       v
Streamlit UI

Evaluation: retrieval metrics + optional RAGAS metrics
```

## Dataset

The starter corpus is the WHO publication **Mental Health Gap Action Programme (mhGAP) guideline for mental, neurological and substance use disorders, Third edition (2023)**. WHO lists it as a 184-page guideline published on 20 November 2023.

- [Official WHO publication page](https://www.who.int/publications/i/item/9789240084278)
- [Dataset setup instructions](dataset/README.md)
- [Dataset manifest](dataset/manifest.json)

The PDF is intentionally **not committed to this repository**. Run the download script after reviewing the licensing information. WHO's publication page states that the 2023 work is available under the CC BY-NC-SA 3.0 IGO licence: non-commercial reuse is permitted subject to attribution and share-alike conditions; commercial use requires permission. Check the source page and licence before every redistribution or commercial use. This repository links to the source rather than redistributing the PDF.

The pipeline accepts additional PDF guidelines. Put them in `dataset/pdfs/`; do not commit large or copyrighted PDFs unless you have the rights to do so.

## Requirements

- Python 3.10 or 3.11 (Python 3.11 recommended).
- 8 GB RAM recommended for ingestion and embeddings; more RAM is helpful for local LLM inference.
- Internet connection for the first-time embedding model download and dataset download.
- Ollama is optional. Without it, the app returns retrieved evidence snippets rather than inventing an answer.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/clinical-protocol-rag.git
cd clinical-protocol-rag
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download the starter dataset

```bash
python dataset/download_dataset.py
```

Read `dataset/README.md` first. The script downloads the official WHO PDF into `dataset/pdfs/`.

### 5. Build the vector database

```bash
python -m src.cli ingest
```

The first run downloads the embedding model from Hugging Face. The generated ChromaDB files are stored locally under `storage/chroma/` and are excluded from Git.

### 6. (Optional) Install and run a local LLM

Install [Ollama](https://ollama.com/), then:

```bash
ollama pull llama3.2:3b
ollama serve
```

In another terminal:

```bash
ollama run llama3.2:3b
```

The application calls the Ollama HTTP API at `http://localhost:11434`. Configure another model or endpoint in `.env` if needed. A local model can require substantial RAM; smaller quantized models may be more suitable for modest hardware.

### 7. Launch the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. Ask a question such as:

> What does the guideline recommend for the management of depression?

The answer panel displays the retrieved source passages and their PDF page numbers. The system should explicitly abstain when the retrieved evidence is insufficient.

## Configuration

Copy `.env.example` to `.env` and adjust values if needed.

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `CHROMA_PATH` | `storage/chroma` | Persistent vector database path |
| `COLLECTION_NAME` | `clinical_guidelines` | ChromaDB collection |
| `CHUNK_SIZE` | `1000` | Chunk size in characters |
| `CHUNK_OVERLAP` | `150` | Character overlap |
| `TOP_K` | `5` | Number of retrieved chunks |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.2:3b` | Local generation model |
| `MIN_RELEVANCE_DISTANCE` | `1.25` | Conservative cosine-distance cutoff; tune on validation data |
| `USE_LLM` | `true` | Use Ollama when available |

The relevance cutoff is a configurable heuristic, not a clinically validated threshold. Calibrate it with a representative evaluation set.

## Adding more documents

1. Obtain clinical guidelines from an authoritative source and check their licences.
2. Put PDFs in `dataset/pdfs/`.
3. Run `python -m src.cli ingest --reset` to rebuild the collection.
4. Keep document titles, source URLs, publication dates and licence information in `dataset/manifest.json`.
5. Do not mix superseded and current guidelines without clearly recording their versions.

For very large corpora, ingestion can be run incrementally in a future extension. The current `--reset` workflow deliberately rebuilds the collection to avoid stale or duplicated chunks.

## Evaluation

Run the local, no-API evaluation:

```bash
python -m src.cli evaluate
```

This reports retrieval-oriented measurements on the small, manually curated benchmark in `evaluation/qa_pairs.json`. The benchmark is a starter set and must be reviewed by a subject-matter expert before drawing meaningful conclusions.

Optional RAGAS evaluation:

```bash
pip install -r requirements-ragas.txt
```

See `evaluation/README.md` for the optional local Ollama-based workflow. RAGAS metrics that require an LLM are not automatically free of compute cost: this setup uses a local model, so there is no per-token API charge, but inference consumes local resources.

### Results status

| Metric | Status | Notes |
|---|---|---|
| Faithfulness | Not measured yet | Run the optional RAGAS evaluation |
| Answer relevancy | Not measured yet | Run the optional RAGAS evaluation |
| Context precision | Not measured yet | Run the optional RAGAS evaluation |
| Retrieval hit rate | Not measured yet | Run the local benchmark |
| MRR@k | Not measured yet | Run the local benchmark |

**No evaluation scores are fabricated or presented as experimental results.** Populate this table only with values produced by an actual run. Record the model, dataset version, benchmark size, date, and configuration alongside every result.

## Testing

```bash
pytest -q
```

The unit tests cover text chunking, PDF extraction metadata, retrieval helpers, and safe fallback behavior. Integration tests requiring downloaded models, ChromaDB, or Ollama are clearly separated from lightweight unit tests.

## Repository structure

```text
clinical-protocol-rag/
├── app.py
├── src/
│   ├── cli.py
│   └── clinical_rag/
│       ├── config.py
│       ├── ingestion.py
│       ├── vector_store.py
│       ├── retrieval.py
│       ├── generation.py
│       └── pipeline.py
├── dataset/
│   ├── README.md
│   ├── manifest.json
│   └── download_dataset.py
├── evaluation/
│   ├── README.md
│   ├── qa_pairs.json
│   ├── evaluate_retrieval.py
│   └── ragas_eval.py
├── tests/
├── reports/
│   └── technical_report.md
├── requirements.txt
├── requirements-ragas.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Limitations and responsible use

- Retrieval quality depends on PDF text quality, chunking, embedding model, and corpus coverage.
- Scanned PDFs may require OCR; OCR is not enabled in this baseline.
- PDF page numbers are physical PDF page indices (1-based), which may differ from printed page labels.
- Similarity is not proof of correctness. Always inspect cited passages.
- The assistant can miss relevant evidence or retrieve outdated recommendations.
- The generation model may still make mistakes. The prompt and evidence display reduce risk but do not eliminate hallucinations.
- This prototype is not validated for clinical use, and it must not be used for patient-specific recommendations.
- The starter WHO publication is mental-health focused; it does not represent all medical specialties.

## Roadmap

- OCR support for scanned guideline PDFs.
- Hybrid retrieval (BM25 + dense vectors) and reranking.
- Incremental document indexing and document version management.
- More diverse, expert-reviewed evaluation questions.
- Improved printed-page-label detection.
- Multilingual retrieval and answer generation.
- Docker packaging and CI workflow.

## References

1. World Health Organization. (2023). *Mental Health Gap Action Programme (mhGAP) guideline for mental, neurological and substance use disorders* (3rd ed.). https://www.who.int/publications/i/item/9789240084278
2. Chroma. https://docs.trychroma.com/
3. Sentence Transformers. https://www.sbert.net/
4. Ollama. https://ollama.com/
5. RAGAS. https://docs.ragas.io/

## License

The software code in this repository is released under the MIT License. This software licence does not apply to third-party documents, models, or datasets. Their original licences remain applicable.
