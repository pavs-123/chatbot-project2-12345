"""
Type 3: Multi-Query RAG
- Expand the user's question into multiple phrasings
- Retrieve docs for each variant
- Merge and answer
"""
from __future__ import annotations
from typing import List
from rag.types.common import setup


def _expand_queries(llm, question: str, n: int = 3) -> List[str]:
    prompt = (
        "Generate " + str(n) + " alternative phrasings capturing different angles of the question.\n"
        "Return each on a new line without numbering.\nQuestion: " + question
    )
    txt = llm.invoke(prompt).content if hasattr(llm, 'invoke') else llm(prompt)
    return [line.strip(" -•\t") for line in txt.splitlines() if line.strip()]


def run(question: str = "What are OpenAI embeddings used for?", reingest: bool = False):
    cfg, retriever, llm = setup(reingest=reingest)
    if not retriever:
        return
    variants = _expand_queries(llm, question, n=3)
    seen = {}
    all_docs = []
    for q in [question] + variants:
        for d in retriever.invoke(q):
            key = getattr(d, 'metadata', {}).get('source','') + '|' + getattr(d, 'page_content','')[:120]
            if key in seen:
                continue
            seen[key] = True
            all_docs.append(d)

    # Build short answer using combined context
    context = "\n\n".join(getattr(d, 'page_content','') for d in all_docs[:6])
    prompt = (
        "Use the context to answer briefly. If unsure, say you don't know.\n"
        f"Question: {question}\n\nContext:\n{context}"
    )
    ans = llm.invoke(prompt).content if hasattr(llm, 'invoke') else llm(prompt)
    print("\n[Multi-Query RAG] Question:", question)
    print("Answer:\n", ans)


if __name__ == "__main__":
    run()
