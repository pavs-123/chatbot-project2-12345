import argparse
from pathlib import Path
from typing import Any

from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain

from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def main():
    parser = argparse.ArgumentParser(description="Simple RAG (Chroma + OpenAI)")
    parser.add_argument("--query", required=True, help="User query to answer")
    parser.add_argument("--reingest", action="store_true", help="Rebuild the vector DB from docs")
    parser.add_argument("--k", type=int, default=None, help="Top K docs to retrieve (override config)")
    args = parser.parse_args()

    cfg = RAGConfig()
    cfg.ensure_dirs()

    if not cfg.openai_api_key:
        print("OPENAI_API_KEY not set. Please add it to .env or your environment.")
        return 1

    embeddings = OpenAIEmbeddings(model=cfg.embedding_model)
    vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, args.reingest, embeddings)

    k = args.k if args.k is not None else cfg.top_k
    retriever = get_retriever(vectorstore, k=k)

    llm = ChatOpenAI(model=cfg.chat_model, temperature=0)
    chain = build_rag_chain(retriever, llm)

    print("=" * 60)
    print("RAG Query:", args.query)
    print("Top K:", k)
    print("DB:", cfg.persist_dir)
    print("Docs:", cfg.docs_dir)
    print("=" * 60)

    answer = chain.invoke(args.query)
    print("\nAnswer:\n", answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
