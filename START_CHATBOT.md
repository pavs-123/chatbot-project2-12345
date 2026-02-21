# 🚀 Quick Start - Chatbot

## Current Status

✅ **All files are present and complete!**
⚠️ **Virtual environment needs fixing** (package corruption)

---

## 🔥 Quick Fix (3 Steps)

### Step 1: Close Everything
- Close VSCode
- Close all terminals
- Close any Python processes

### Step 2: Run Fix Script
```powershell
# Open a NEW PowerShell window and run:
.\fix_and_run.ps1
```

This will:
- Remove corrupted .venv
- Create fresh environment
- Install all dependencies
- Test everything
- Start the server

### Step 3: Open Browser
```
http://localhost:8001
```

---

## 🎯 Alternative: Manual Fix

If the script doesn't work:

```powershell
# 1. Delete .venv folder manually (use File Explorer if command fails)
Remove-Item -Recurse -Force .venv

# 2. Create new environment
python -m venv .venv

# 3. Activate
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
uv sync
# OR if uv fails:
pip install -e .

# 5. Start server
uvicorn chatbot.api:app --reload --port 8001
```

---

## 💰 Free Option: Use Ollama Instead of OpenAI

Don't want to use your OpenAI API key?

```powershell
# 1. Install Ollama from https://ollama.ai/download

# 2. Start Ollama
ollama serve

# 3. Pull models (in another terminal)
ollama pull llama3.2
ollama pull nomic-embed-text

# 4. Update .env
CHATBOT_LLM_PROVIDER=ollama

# 5. Start chatbot
uvicorn chatbot.api:app --reload --port 8001
```

---

## 📦 What You Already Have

### Complete Chatbot Features
✅ RAG with ChromaDB vector store
✅ Weather integration (Open-Meteo API)
✅ LangGraph for intent routing
✅ Web UI (HTML + JavaScript)
✅ REST API endpoints
✅ WebSocket support
✅ Server-Sent Events (SSE) streaming
✅ OpenAI + Ollama support
✅ Environment configuration
✅ Sample documents for testing

### Files Structure
```
chatbot/
├── api.py              # FastAPI server
├── graph.py            # LangGraph flow
├── llm_provider.py     # LLM abstraction
└── static/
    └── index.html      # Web UI

rag/
├── config.py           # RAG configuration
├── ingest.py           # Document loading
├── retriever.py        # Retrieval logic
├── chain.py            # RAG chain
└── sample_docs/        # Test documents

mcp_weather/            # Weather API integration
.env                    # Your API keys (configured)
pyproject.toml          # Dependencies
```

---

## 🧪 Test After Starting

### Test 1: Web UI
Open browser: http://localhost:8001

### Test 2: API Documentation
Open browser: http://localhost:8001/docs

### Test 3: RAG Query
```powershell
curl -X POST http://localhost:8001/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"What is in the sample docs?\"}'
```

### Test 4: Weather Query
```powershell
curl -X POST http://localhost:8001/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"What is the weather in Paris?\"}'
```

---

## ❓ Need Help?

Read the full guide: **SETUP_CHATBOT.md**

**Common Issues:**
1. **"Access Denied" when deleting .venv** → Close ALL Python processes first
2. **"Cannot import langchain_core"** → Environment still corrupted, delete .venv manually
3. **"OPENAI_API_KEY not set"** → Check .env file exists and has your key
4. **Ollama connection error** → Run `ollama serve` in another terminal

---

## ✨ Summary

**You DON'T need any additional files!**

Everything is ready - you just need to **fix the virtual environment**.

Run: `.\fix_and_run.ps1`

That's it! 🎉
