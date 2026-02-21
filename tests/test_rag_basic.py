import os
import pytest

def test_imports_ok():
    import rag.config as config
    import rag.ingest as ingest
    import rag.retriever as retriever
    import rag.chain as chain
    assert hasattr(config, 'RAGConfig')
    assert hasattr(ingest, 'build_or_load_vectorstore')
    assert hasattr(retriever, 'get_retriever')
    assert hasattr(chain, 'build_rag_chain')

@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason='Requires OpenAI API key')
def test_builds_chain_end_to_end(tmp_path):
    from rag.config import RAGConfig
    from rag.ingest import build_or_load_vectorstore
    from rag.retriever import get_retriever
    from rag.chain import build_rag_chain
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    cfg = RAGConfig()
    cfg.ensure_dirs()
    embeddings = OpenAIEmbeddings(model=cfg.embedding_model)
    vs = build_or_load_vectorstore(cfg.docs_dir, tmp_path / 'db', True, embeddings)
    retr = get_retriever(vs, k=2)
    llm = ChatOpenAI(model=cfg.chat_model, temperature=0)
    chain = build_rag_chain(retr, llm)
    assert chain is not None
