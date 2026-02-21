"""
Type 1: Naive RAG (Retrieve-then-Read)
- Retrieve top-k docs for a question
- Feed docs + question to the LLM with a simple prompt
- Good baseline, easiest to understand
"""
from __future__ import annotations
from rag.types.common import setup
from rag.chain import build_rag_chain


def run(question: str = "What is RAG?", reingest: bool = False):
    cfg, retriever, llm = setup(reingest=reingest)
    if not retriever:
        return
    chain = build_rag_chain(retriever, llm)
    print("\n[Naive RAG] Question:", question)
    print("Answer:\n", chain.invoke(question))


if __name__ == "__main__":
    run()
