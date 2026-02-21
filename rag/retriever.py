from typing import Optional


def get_retriever(vectorstore, k: int = 4, score_threshold: Optional[float] = None):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    if score_threshold is not None:
        retriever.search_kwargs["score_threshold"] = score_threshold
    return retriever
