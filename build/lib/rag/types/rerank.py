"""
Type 2: RAG with simple reranking
- Retrieve top-k docs
- Optionally ask the LLM to score each doc's relevance briefly
- Reorder by score, then answer using top docs
Note: For simplicity, we implement a lightweight rerank using the LLM.
"""
from __future__ import annotations
from typing import List, Tuple
from rag.types.common import setup


def _score_docs_with_llm(llm, question: str, docs: List):
    prompt = (
        "Score each document from 0-10 for relevance to the question.\n"
        "Question: " + question + "\n\n" +
        "Documents:\n" +
        "\n\n".join(f"Doc {i+1}: {getattr(d, 'page_content','')[:500]}" for i, d in enumerate(docs)) +
        "\n\nReturn lines in format: Doc i: score"
    )
    txt = llm.invoke(prompt).content if hasattr(llm, 'invoke') else llm(prompt)
    scores = []
    for line in txt.splitlines():
        line = line.strip()
        if line.lower().startswith("doc ") and ":" in line:
            try:
                left, right = line.split(":", 1)
                idx = int(left.split()[1]) - 1
                score = float(right.strip().split()[0])
                scores.append((idx, score))
            except Exception:
                continue
    return scores


def run(question: str = "What is Chroma?", reingest: bool = False):
    cfg, retriever, llm = setup(reingest=reingest)
    if not retriever:
        return
    # Pull more docs, then rerank
    retriever.search_kwargs["k"] = max(retriever.search_kwargs.get("k", 4), 6)
    docs = retriever.invoke(question)
    scored = _score_docs_with_llm(llm, question, docs)
    order = sorted(((s, i) for i, s in scored), reverse=True)
    reranked = [docs[i] for _, i in order][:4] if order else docs[:4]

    # Simple answer using top reranked docs
    context = "\n\n".join(getattr(d, 'page_content','') for d in reranked)
    prompt = (
        "Use the context to answer briefly. If unsure, say you don't know.\n"
        f"Question: {question}\n\nContext:\n{context}"
    )
    ans = llm.invoke(prompt).content if hasattr(llm, 'invoke') else llm(prompt)
    print("\n[RAG + Rerank] Question:", question)
    print("Answer:\n", ans)


if __name__ == "__main__":
    run()
