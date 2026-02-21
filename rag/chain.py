from typing import Any, List

# Avoid importing langchain modules at import time; we import lazily in functions


def _format_docs(docs: List[Any]) -> str:
    return "\n\n".join(f"[Source: {getattr(d, 'metadata', {}).get('source','')}]:\n{getattr(d, 'page_content', '')}" for d in docs)


def build_rag_chain(retriever, llm, chat_history: str = None):
    try:
        from langchain_core.runnables import RunnableLambda, RunnablePassthrough
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
    except Exception as e:
        raise RuntimeError(
            "langchain_core is required to build the RAG chain. Install langchain-core."
        ) from e

    # Enhanced prompt with conversation history
    system_msg = "You are a helpful assistant. Use the provided context to answer briefly. If unsure, say you don't know."
    if chat_history:
        system_msg += f"\n\n{chat_history}"
    
    prompt_tmpl = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Question: {question}\\n\\nContext:\\n{context}")
    ])

    chain = (
        {"question": RunnablePassthrough(), "context": retriever | RunnableLambda(_format_docs)}
        | prompt_tmpl
        | llm
        | StrOutputParser()
    )
    return chain
