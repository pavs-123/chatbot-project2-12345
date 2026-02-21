from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class RAGConfig:
    # Models
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    # Paths
    root_dir: Path = Path(os.getcwd())
    docs_dir: Path = Path(os.getenv("RAG_DOCS_DIR", "rag/sample_docs"))
    persist_dir: Path = Path(os.getenv("RAG_DB_DIR", "rag/chroma_db"))

    # Retrieval
    top_k: int = int(os.getenv("RAG_TOP_K", "4"))

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    def ensure_dirs(self) -> None:
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
