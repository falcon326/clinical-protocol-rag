# Clinical Protocol & Medical Literature Assistant
## Technical Report: Design, Implementation, and Evaluation Plan

**Project type:** End-to-end Retrieval-Augmented Generation (RAG) prototype  
**Domain:** Clinical guidelines and medical literature  
**Primary source:** WHO mhGAP Guideline, Third Edition (2023)  
**Implementation language:** Python

---

## Abstract

This project presents a local-first Retrieval-Augmented Generation (RAG) system for searching clinical guideline documents. The system ingests PDF publications, extracts page-aware text, divides the content into overlapping chunks, encodes those chunks with a sentence-transformer embedding model, and stores the resulting vectors in ChromaDB. At query time, semantic retrieval selects potentially relevant passages. An optional local large language model (LLM), served through Ollama, produces a response constrained to the retrieved evidence. The interface exposes source filenames and physical PDF page numbers to support inspection and traceability.

The initial corpus is the World Health Organization's 2023 third edition of the mhGAP guideline, a 184-page publication addressing mental, neurological and substance-use conditions. The implementation is designed to accept additional PDFs without changing the core pipeline. A local retrieval benchmark and an optional RAGAS evaluation workflow are included. No performance scores are claimed before the experiments have actually been executed.

**Scope limitation:** The prototype is an educational literature-search tool. It is not validated for clinical use and must not be used for diagnosis, treatment, triage, or patient-specific decision-making.

## 1. Introduction

Clinical recommendations are distributed across long documents, technical guidelines, and evidence summaries. Finding the passage relevant to a focused question can require manual searching across many pages. A document-grounded retrieval assistant can make this process more efficient by locating semantically relevant passages and presenting them with source metadata.

A conventional language model may generate plausible statements that are not supported by a particular guideline. RAG addresses this risk by retrieving external evidence at inference time and providing that evidence to the generation model. However, RAG does not guarantee correctness: retrieval may fail, documents may be outdated, and generated statements may misinterpret evidence. This project therefore emphasizes traceable sources, conservative abstention, and explicit evaluation.

## 2. Objectives

The main objectives are:

1. Build a repeatable PDF ingestion pipeline.
2. Preserve source filename and physical PDF page number throughout processing.
3. Generate semantic embeddings locally.
4. Persist vectors in ChromaDB.
5. Retrieve relevant passages for a natural-language question.
6. Generate answers from retrieved evidence only, when a local LLM is available.
7. Provide an extractive evidence fallback when generation is unavailable.
8. Expose the workflow through a Streamlit interface.
9. Evaluate retrieval behavior and provide an optional RAGAS workflow.
10. Keep the project reproducible and suitable for a public GitHub repository.

## 3. Dataset and provenance

### 3.1 Selected document

The starter corpus uses:

- **Title:** Mental Health Gap Action Programme (mhGAP) guideline for mental, neurological and substance use disorders
- **Publisher:** World Health Organization
- **Edition:** Third edition
- **Publication date:** 20 November 2023
- **Length:** 184 pages
- **ISBN:** 9789240084278
- **Official page:** https://www.who.int/publications/i/item/9789240084278

The document was selected because it is an authoritative, structured guideline with a clearly identified edition and publication date. Its subject matter provides a coherent initial domain for testing document retrieval and page-level citation.

### 3.2 Licensing and data handling

The WHO publication page identifies the 2023 publication as CC BY-NC-SA 3.0 IGO. The repository does not include the PDF binary. Instead, it includes a manifest and a downloader that retrieves the publication from the WHO-hosted endpoint. Users must review the source licence and attribution requirements before reuse. Commercial use requires permission under the stated terms. The software licence in this repository does not override the source document's licence.

### 3.3 Corpus limitations

The initial corpus is intentionally narrow and focuses on mental, neurological, and substance-use conditions. It cannot represent all clinical specialties or all current recommendations. Future corpus expansion should prioritize authoritative sources, edition tracking, and licence verification.

## 4. System architecture

The pipeline consists of six main stages:

1. **Ingestion:** enumerate PDF files in `dataset/pdfs/`.
2. **Extraction:** use PyMuPDF to extract text page by page.
3. **Chunking:** split extracted text into bounded segments with overlap.
4. **Embedding and indexing:** encode chunks using `all-MiniLM-L6-v2` and store vectors and metadata in ChromaDB.
5. **Retrieval and generation:** encode a user question, retrieve top-k passages, and optionally pass them to an Ollama model.
6. **Presentation:** display the answer, response mode, evidence passages, source filenames, and PDF page numbers in Streamlit.

### 4.1 Page-aware extraction

Each non-empty PDF page is represented as a record containing its extracted text, source filename, title, and one-based physical PDF page index. This metadata is copied into every chunk created from that page.

The page number shown by the application is the physical PDF page index. It may not match a printed page number visible inside the document, especially where front matter uses Roman numerals.

### 4.2 Chunking

The baseline uses character-bounded chunks with configurable overlap. Overlap helps retain context near chunk boundaries. The default configuration is:

- Chunk size: 1,000 characters.
- Overlap: 150 characters.

These are starting parameters, not empirically optimized values. A rigorous experiment should compare multiple chunk sizes and overlap settings using the same evaluation questions.

### 4.3 Embeddings and vector database

The `sentence-transformers/all-MiniLM-L6-v2` model maps text into dense semantic vectors. ChromaDB stores the vectors, text, and metadata persistently. Cosine distance is used for nearest-neighbor retrieval.

The baseline uses dense semantic retrieval only. Hybrid lexical-semantic retrieval and reranking are reserved for future work.

### 4.4 Grounded generation

When Ollama is available, the system sends the question and retrieved evidence to a local LLM. The system prompt requires evidence-only answers and source/page citations. It also prohibits diagnosis, prescribing, and patient-specific treatment advice.

If the LLM is unavailable, the system returns retrieved excerpts rather than attempting an unsupported synthesis. If no sufficiently relevant passages are retrieved, the system abstains.

This behavior is a risk-reduction measure, not a proof that every generated statement is supported. The cited passages must still be reviewed.

## 5. Implementation

The project is organized into small modules:

| Module | Responsibility |
|---|---|
| `ingestion.py` | PDF extraction, normalization, chunking |
| `vector_store.py` | Embedding generation and ChromaDB persistence |
| `retrieval.py` | Semantic retrieval and distance filtering |
| `generation.py` | Ollama generation and extractive fallback |
| `pipeline.py` | Ingestion and query orchestration |
| `cli.py` | Command-line entry points |
| `app.py` | Streamlit user interface |

The application is local-first. The embedding model is downloaded on first use and then executed locally. Ollama runs a local generation model. There is no requirement for a paid inference API.

## 6. Evaluation methodology

Evaluation must distinguish retrieval quality from generation quality.

### 6.1 Retrieval benchmark

The included starter benchmark records expected source documents for a small set of questions. It computes:

- **Hit Rate@k:** proportion of questions for which the expected source appears in the retrieved top-k passages.
- **Mean Reciprocal Rank (MRR@k):** average reciprocal rank of the first retrieved expected source.

The current benchmark is a smoke test, not a validated clinical benchmark. It should be expanded with expert-reviewed questions and reference passages tied to specific pages.

### 6.2 RAGAS metrics

An optional RAGAS script is provided for:

- **Faithfulness:** whether claims in an answer are supported by the retrieved context.
- **Answer relevancy:** whether the response addresses the question.
- **Context precision:** whether relevant context is ranked ahead of irrelevant context.

The script is configured to use a local Ollama model as evaluator, avoiding per-token API charges. Local inference still requires compute resources. RAGAS interfaces evolve, so the adapter should be checked against the installed version.

A high faithfulness score is not equivalent to medical correctness. Evaluation should combine automated metrics, expert review, source-version checks, and error analysis.

### 6.3 Results

No experimental values are reported in this initial project package. This is intentional: reporting invented values would be scientifically misleading.

| Metric | Result | Status |
|---|---:|---|
| Faithfulness | — | Pending execution |
| Answer relevancy | — | Pending execution |
| Context precision | — | Pending execution |
| Hit Rate@k | — | Pending execution |
| MRR@k | — | Pending execution |

After executing the evaluation scripts, record the exact model versions, dataset edition, benchmark size, parameters, date, and results in the main README and this report.

## 7. Reproducibility

The repository includes:

- Dependency lists.
- Environment-variable template.
- Dataset manifest and download script.
- CLI commands for ingestion and evaluation.
- Unit tests for chunking, PDF extraction, metadata, and fallback behavior.
- A Git ignore policy for downloaded PDFs, model artifacts, local vector storage, and secrets.

The first run requires internet access to download the dataset and embedding model. Subsequent retrieval and generation can operate locally, provided the required models and data are already present.

## 8. Limitations and risks

1. **No OCR baseline:** image-only or scanned PDFs may produce no extractable text.
2. **Physical page numbering:** printed page labels are not parsed.
3. **Dense retrieval only:** keyword-sensitive searches may be missed.
4. **Distance threshold:** the configured cutoff is heuristic and requires calibration.
5. **Model dependence:** a local LLM can omit, misinterpret, or overstate evidence.
6. **Limited evaluation set:** the starter questions are too few for robust conclusions.
7. **Narrow corpus:** the starter guideline does not cover all specialties.
8. **Guideline currency:** users must verify that the retrieved edition remains current.
9. **No clinical validation:** the system is not a medical device or clinical decision-support product.

## 9. Future work

- OCR with explicit page provenance.
- Hybrid retrieval combining BM25 and dense vectors.
- Cross-encoder reranking.
- Document-level version and update management.
- Better detection of printed page labels.
- A larger expert-reviewed question-answer benchmark.
- Error analysis by retrieval failure, unsupported generation, and citation mismatch.
- Containerization and continuous integration.
- Additional guideline sources after licence and provenance review.

## 10. Conclusion

This project implements a reproducible baseline for source-grounded question answering over clinical guideline PDFs. It combines page-aware PDF processing, local embeddings, persistent vector search, optional local LLM generation, and a visible evidence trail. Its primary engineering contribution is an end-to-end and inspectable RAG workflow rather than a claim of clinical performance.

The system should be treated as a research and portfolio prototype. Any future extension toward clinical workflows would require substantial validation, governance, security, and regulatory assessment.

## References

1. World Health Organization. (2023). *Mental Health Gap Action Programme (mhGAP) guideline for mental, neurological and substance use disorders* (3rd ed.). https://www.who.int/publications/i/item/9789240084278
2. Chroma documentation. https://docs.trychroma.com/
3. Sentence Transformers documentation. https://www.sbert.net/
4. Ollama documentation. https://ollama.com/
5. RAGAS documentation. https://docs.ragas.io/
6. PyMuPDF documentation. https://pymupdf.readthedocs.io/
