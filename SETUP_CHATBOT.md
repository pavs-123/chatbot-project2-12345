# Chatbot Setup Guide

## ✅ What You Have

Your chatbot is **complete** with all necessary files:

### Core Chatbot Files
- ✅ `chatbot/api.py` - FastAPI server with REST & WebSocket endpoints
- ✅ `chatbot/graph.py` - LangGraph flow for intent routing (weather + RAG)
- ✅ `chatbot/llm_provider.py` - Flexible LLM provider (OpenAI or Ollama)
- ✅ `chatbot/static/index.html` - Web UI for the chatbot

### RAG Components
- ✅ `rag/config.py` - Configuration
- ✅ `rag/ingest.py` - Document loading & vector store
- ✅ `rag/retriever.py` - Retrieval logic
- ✅ `rag/chain.py` - RAG chain builder
- ✅ `rag/sample_docs/` - Sample documents for testing

### Weather Integration
- ✅ `mcp_weather/` - Weather API integration (Open-Meteo)

### Configuration
- ✅ `pyproject.toml` - Project dependencies
- ✅ `.env` - Environment variables (API keys configured)
- ✅ `.env.example` - Template for new setups

---

## ⚠️ Current Issue

Your virtual environment has **corrupted packages** (likely from locked files during installation).

**Error:** `ImportError: cannot import name 'LanguageModelInput' from 'langchain_core.language_models'`

---

## 🔧 How to Fix

### Option 1: Fresh Virtual Environment (Recommended)

**Close ALL Python processes, VSCode, terminals, then:**

```powershell
# Close this terminal and open a NEW PowerShell/CMD window

# 1. Delete old environment (manually if command fails)
Remove-Item -Recurse -Force .venv

# 2. Create fresh environment
python -m venv .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# 4. Install using uv
uv sync

# 5. Test installation
python -c "from chatbot.api import app; print('✅ Success!')"
```

### Option 2: Use Ollama (Free, No API Key Needed)

If you want to avoid OpenAI costs:

1. **Install Ollama:** https://ollama.ai/download
2. **Start Ollama:**
   ```powershell
   ollama serve
   ```
3. **Pull a model:**
   ```powershell
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```
4. **Update .env:**
   ```env
   CHATBOT_LLM_PROVIDER=ollama
   ```

---

## 🚀 Running the Chatbot

Once packages are fixed:

```powershell
# Start the server
uvicorn chatbot.api:app --reload --port 8001

# Or use the provided script
python -m chatbot.api
```

**Access:**
- Web UI: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

---

## 📋 API Endpoints

### 1. POST /chat
```json
{
  "message": "What is RAG?",
  "reingest": false,
  "top_k": 4
}
```

### 2. GET /chat/stream
Server-Sent Events for streaming responses

### 3. WebSocket /ws/chat
Real-time bidirectional chat

---

## 🧪 Test Examples

### RAG Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is in the sample docs?"}'
```

### Weather Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in London?"}'
```

---

## 📝 Environment Variables

Required in `.env`:

```env
# LLM Provider: "openai" or "ollama"
CHATBOT_LLM_PROVIDER=openai

# For OpenAI (required if using openai provider)
OPENAI_API_KEY=your-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# For Ollama (required if using ollama provider)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text

# RAG Configuration
RAG_DOCS_DIR=rag/sample_docs
RAG_DB_DIR=rag/chroma_db
RAG_TOP_K=4
```

---

## 🎯 Features

1. **Intent Detection** - Automatically routes weather vs RAG queries
2. **RAG Pipeline** - Uses ChromaDB + LangChain for document QA
3. **Weather Integration** - Real-time weather via Open-Meteo API
4. **Flexible LLM** - Supports OpenAI or local Ollama
5. **Multiple Interfaces** - REST API, SSE streaming, WebSocket
6. **Web UI** - Beautiful chat interface included

---

## ❓ Do You Need Any Additional Files?

**No!** You have everything needed. Just need to fix the environment.

**Missing from most projects but you have:**
- ✅ Web UI (index.html)
- ✅ Environment config (.env.example)
- ✅ LLM provider flexibility (OpenAI + Ollama)
- ✅ Multiple API interfaces (REST + WebSocket + SSE)
- ✅ Intent routing (LangGraph)
- ✅ Sample documents for testing

---

## 🆘 Quick Fix Command

Run this in a **NEW terminal** (close all Python processes first):

```powershell
# One-liner to fix and test
Remove-Item -Recurse -Force .venv; python -m venv .venv; .\.venv\Scripts\Activate.ps1; uv sync; python -c "from chatbot.api import app; print('✅ Ready to run!')"
```

Then start:
```powershell
uvicorn chatbot.api:app --reload --port 8001
```
