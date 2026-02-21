"""
Run a tour of RAG types from basic to a bit more advanced.
Usage examples:
  python rag/types/run_all.py --reingest
  python rag/types/run_all.py --type naive --query "What is RAG?"
"""
from __future__ import annotations
import argparse

from rag.types import naive, rerank, multiquery, map_reduce


def main():
    p = argparse.ArgumentParser(description="RAG types tour")
    p.add_argument("--type", choices=["naive", "rerank", "multiquery", "map_reduce", "all"], default="all")
    p.add_argument("--query", default=None, help="Custom question")
    p.add_argument("--reingest", action="store_true", help="Rebuild the vector DB")
    args = p.parse_args()

    if args.type in ("naive", "all"):
        naive.run(question=args.query or "What is RAG?", reingest=args.reingest)
    if args.type in ("rerank", "all"):
        rerank.run(question=args.query or "What is Chroma?", reingest=False)
    if args.type in ("multiquery", "all"):
        multiquery.run(question=args.query or "What are OpenAI embeddings used for?", reingest=False)
    if args.type in ("map_reduce", "all"):
        map_reduce.run(question=args.query or "Summarize the sample docs.", reingest=False)


if __name__ == "__main__":
    main()
