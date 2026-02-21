"""
LLM Provider - supports OpenAI and Ollama (local/free)

Set CHATBOT_LLM_PROVIDER env var:
  - "openai" (default, requires OPENAI_API_KEY)
  - "ollama" (free, local, requires Ollama running)

For Ollama:
  1. Install: https://ollama.ai/download
  2. Start: ollama serve
  3. Pull model: ollama pull llama3.2 (or mistral, phi3, etc.)
"""
import os
from typing import Any


def get_llm(model_override: str | None = None) -> Any:
    """
    Get an LLM instance based on CHATBOT_LLM_PROVIDER.
    
    Args:
        model_override: Optional model name to override defaults
    
    Returns:
        LLM instance (ChatOpenAI or ChatOllama)
    """
    provider = os.getenv("CHATBOT_LLM_PROVIDER", "openai").lower()
    
    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise RuntimeError(
                "langchain-ollama is required for Ollama. Install: pip install langchain-ollama"
            )
        model = model_override or os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=0.7)
    
    else:  # default to openai
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise RuntimeError(
                "langchain-openai is required for OpenAI. Install: pip install langchain-openai"
            )
        model = model_override or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when using OpenAI provider. "
                "Set it in .env or switch to CHATBOT_LLM_PROVIDER=ollama"
            )
        return ChatOpenAI(model=model, api_key=api_key, temperature=0.7)


def get_embeddings(provider_override: str | None = None) -> Any:
    """
    Get embeddings instance.
    
    For Ollama: uses OllamaEmbeddings (local, free)
    For OpenAI: uses OpenAIEmbeddings
    """
    provider = provider_override or os.getenv("CHATBOT_LLM_PROVIDER", "openai").lower()
    
    if provider == "ollama":
        try:
            from langchain_ollama import OllamaEmbeddings
        except ImportError:
            raise RuntimeError(
                "langchain-ollama is required. Install: pip install langchain-ollama"
            )
        model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaEmbeddings(model=model, base_url=base_url)
    
    else:  # openai
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise RuntimeError(
                "langchain-openai is required. Install: pip install langchain-openai"
            )
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY required for OpenAI embeddings")
        return OpenAIEmbeddings(model=model, api_key=api_key)
