"""
Type 4: Map-Reduce Style RAG (summarize parts then combine)
- Retrieve docs
- Map: Summarize each doc briefly
- Reduce: Combine summaries into a final concise answer
"""
from __future__ import annotations
from rag.types.common import setup


def run(question: str = "Summarize the sample docs.", reingest: bool = False):
    cfg, retriever, llm = setup(reingest=reingest)
    if not retriever:
        return
    docs = retriever.invoke(question)

    # Map step: summarize each doc
    summaries = []
    for d in docs:
        prompt = (
            "Summarize this document in one sentence focusing on information relevant to the question.\n"
            f"Question: {question}\n\nDocument:\n{getattr(d, 'page_content','')}\n"
        )
        summaries.append(llm.invoke(prompt).content if hasattr(llm, 'invoke') else llm(prompt))

    # Reduce step: combine summaries into an answer
    reduce_prompt = (
        "Using these summaries, produce a brief, helpful answer. If unsure, say you don't know.\n"
        "Summaries:\n" + "\n".join(f"- {s}" for s in summaries)
    )
    ans = llm.invoke(reduce_prompt).content if hasattr(llm, 'invoke') else reduce_prompt

    print("\n[Map-Reduce RAG] Question:", question)
    print("Answer:\n", ans)


if __name__ == "__main__":
    run()
