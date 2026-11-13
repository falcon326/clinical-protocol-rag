"""Streamlit interface for the Clinical Protocol RAG assistant."""
import streamlit as st
from src.clinical_rag.pipeline import ask
from src.clinical_rag.vector_store import VectorStore
from src.clinical_rag.config import settings

st.set_page_config(page_title="Clinical Protocol RAG", page_icon="📚", layout="wide")
st.title("Clinical Protocol & Medical Literature Assistant")
st.caption("A source-grounded research prototype powered by local embeddings, ChromaDB and optional Ollama.")

with st.sidebar:
    st.header("System status")
    st.write(f"**Embedding model:** `{settings.embedding_model}`")
    st.write(f"**Vector collection:** `{settings.collection_name}`")
    st.write(f"**Generation model:** `{settings.ollama_model}`")
    st.write(f"**Top-k retrieval:** `{settings.top_k}`")
    st.divider()
    st.warning(
        "Educational research tool only. Not for diagnosis, treatment, triage, "
        "or patient-specific clinical decisions."
    )

@st.cache_resource
def get_store():
    return VectorStore()

question = st.text_area(
    "Ask a question about the indexed clinical guidelines",
    placeholder="What recommendations does the guideline provide for depression?",
    height=100,
)
if st.button("Search the guidelines", type="primary", disabled=not question.strip()):
    try:
        with st.spinner("Retrieving evidence and preparing the response..."):
            result = ask(question, get_store())
        st.subheader("Answer")
        st.markdown(result["answer"])
        st.caption(f"Response mode: {result['mode']}")
        st.subheader("Retrieved evidence")
        if not result["evidence"]:
            st.info("No sufficiently relevant evidence was retrieved.")
        for index, item in enumerate(result["evidence"], start=1):
            meta = item["metadata"]
            title = meta.get("title", meta.get("source", "Source"))
            with st.expander(
                f"{index}. {title} · PDF page {meta.get('page', 'N/A')} · "
                f"distance {item['distance']:.3f}",
                expanded=index == 1,
            ):
                st.write(item["text"])
                st.caption(f"File: {meta.get('source')} | Chunk: {meta.get('chunk_index')}")
    except Exception as exc:
        st.error(f"Application error: {exc}")
        st.info("Confirm that the dataset has been downloaded and indexed.")
