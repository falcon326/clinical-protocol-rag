# Evaluation protocol

## 1. Local retrieval benchmark

Run:

```bash
python -m src.cli evaluate
```

The benchmark checks whether the expected source document appears in the retrieved top-k results and calculates hit rate and mean reciprocal rank (MRR). It is a retrieval smoke test, not a clinical accuracy study. The included questions are intentionally small and broad; expand them with expert-reviewed questions and page-grounded reference answers before reporting research-grade results.

## 2. RAGAS evaluation (optional)

RAGAS can assess dimensions such as faithfulness and answer relevancy. These metrics require model judgments and should be interpreted alongside human review. A local Ollama judge avoids paid API calls, but inference still uses local compute and may be slow.

Install the optional dependencies:

```bash
pip install -r requirements-ragas.txt
```

Make sure Ollama is running and the configured model is available:

```bash
ollama pull llama3.2:3b
ollama serve
```

Then run:

```bash
python evaluation/ragas_eval.py
```

The script uses the current local vector index and the small benchmark. RAGAS APIs can change between releases; if an API incompatibility occurs, consult the installed RAGAS version's documentation and update the adapter. Do not report scores unless the run completes successfully.

## 3. Metrics

- **Faithfulness:** whether response claims are supported by retrieved context.
- **Answer relevancy:** whether the response addresses the question.
- **Context precision:** whether retrieved context is relevant and correctly ranked.
- **Hit rate@k:** fraction of benchmark questions for which the expected source is retrieved.
- **MRR@k:** reciprocal rank of the first retrieved expected source, averaged over questions.

A high faithfulness score does not prove medical correctness. It only measures grounding relative to the supplied context. Include human review, source version checks, and a broader benchmark in any serious evaluation.

## 4. Reporting template

Record:
- Evaluation date and commit hash.
- PDF titles, editions, and file hashes.
- Embedding and generation model names/versions.
- Chunk size, overlap, top-k, and distance threshold.
- Benchmark size and reviewer qualifications.
- Metric values, failure cases, and limitations.

Never fabricate or estimate scores.
