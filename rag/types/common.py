"""
Common helpers for RAG type demos.
They reuse rag.config and rag.ingest to keep things simple and consistent.
"""
from __future__ import annotations
from typing import Optional
from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever


def setup(reingest: bool = False, k: Optional[int] = None):
    """Create embeddings, vectorstore, retriever, and llm.
    Returns (cfg, retriever, llm).
    """
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI

    cfg = RAGConfig()
    cfg.ensure_dirs()

    if not cfg.openai_api_key:
        print("OPENAI_API_KEY not set. Please add it to .env or your environment.")
        return None, None, None

    embeddings = OpenAIEmbeddings(model=cfg.embedding_model)
    vs = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, reingest, embeddings)
    top_k = k if k is not None else cfg.top_k
    retriever = get_retriever(vs, k=top_k)
    llm = ChatOpenAI(model=cfg.chat_model, temperature=0)
    return cfg, retriever, llm
