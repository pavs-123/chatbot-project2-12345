from pathlib import Path
from typing import List

# Lazy imports inside functions to avoid hard dependency errors at import time


def _load_texts(docs_dir: Path):
    try:
        from langchain_core.documents import Document
    except Exception as e:
        raise RuntimeError(
            "langchain_core is required to load documents. Please install langchain-core."
        ) from e

    docs: List[Document] = []  # type: ignore[name-defined]
    for ext in ("*.txt", "*.md"):
        for p in docs_dir.rglob(ext):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            docs.append(Document(page_content=text, metadata={"source": str(p)}))
    return docs


def build_or_load_vectorstore(
    docs_dir: Path,
    persist_dir: Path,
    reingest: bool,
    embedding,
):
    """
    Build or load a Chroma vector store.
    Dependencies (imported lazily when needed):
      - langchain_community (Chroma)
      - chromadb
    """
    try:
        from langchain_community.vectorstores import Chroma  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "langchain-community (and chromadb) are required. Install with: pip install langchain-community chromadb"
        ) from e

    persist_dir.mkdir(parents=True, exist_ok=True)
    if not reingest and any(persist_dir.iterdir()):
        return Chroma(persist_directory=str(persist_dir), embedding_function=embedding)

    # Fresh ingest
    documents = _load_texts(docs_dir)
    if not documents:
        # Create a placeholder doc so vector store exists
        try:
            from langchain_core.documents import Document
        except Exception as e:
            raise RuntimeError(
                "langchain_core is required to create placeholder documents."
            ) from e
        documents = [
            Document(page_content="Sample placeholder document for RAG.", metadata={"source": "placeholder"})
        ]
    vs = Chroma.from_documents(documents, embedding, persist_directory=str(persist_dir))
    vs.persist()
    return vs
