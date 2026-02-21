# 🤖 AI Chatbot - Complete Solution

## 🎯 What Is This?

A **production-ready AI chatbot** with RAG (Retrieval Augmented Generation), weather integration, conversation memory, and a beautiful modern UI.

### ✨ Key Features:

- 🧠 **Conversation Memory** - Remembers context across messages
- 📚 **RAG System** - Answer questions from your documents
- 🌤️ **Weather Integration** - Real-time weather data
- 📤 **Document Upload** - Add files via drag & drop
- 💾 **History Persistence** - Save & export conversations
- 🎨 **Modern UI** - Beautiful gradient design
- ⚡ **One-Click Launch** - No configuration needed
- 🔌 **Flexible LLM** - OpenAI or Ollama (free local)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run the Launcher

**Windows:**
```
Double-click: RUN_CHATBOT.bat
```

**Linux/Mac:**
```bash
bash RUN_CHATBOT.sh
```

**Or Python:**
```bash
python run_chatbot.py
```

### Step 2: Wait for Setup (First Time Only)

The launcher automatically:
- ✅ Checks Python version
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Configures environment
- ✅ Starts server

### Step 3: Open Browser

```
http://localhost:8001
```

**That's it!** 🎉

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│                  Web UI (HTML/JS)               │
│  • Modern gradient design                       │
│  • File upload                                  │
│  • Chat history                                 │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           FastAPI Server (Python)               │
│  • REST API endpoints                           │
│  • WebSocket support                            │
│  • Session management                           │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          LangGraph Flow (Orchestrator)          │
│  • Intent detection                             │
│  • Route: Weather vs RAG                        │
│  • Memory management                            │
└────────┬───────────────────────┬────────────────┘
         │                       │
┌────────▼───────────┐  ┌───────▼────────────────┐
│  Weather Handler   │  │    RAG Handler         │
│  • Open-Meteo API  │  │  • ChromaDB vectors    │
│  • City geocoding  │  │  • LLM chain           │
└────────────────────┘  └───────┬────────────────┘
                                │
                       ┌────────▼────────────┐
                       │  LLM Provider       │
                       │  • OpenAI           │
                       │  • Ollama (local)   │
                       └─────────────────────┘
```

---

## 📁 Project Structure

```
chatbot/
├── api.py              # FastAPI server
├── graph.py            # LangGraph flow
├── llm_provider.py     # LLM abstraction
├── memory.py           # Conversation memory
├── static/
│   └── index.html      # Web UI
├── chat_history/       # Saved conversations
└── uploads/            # User uploaded files

rag/
├── config.py           # RAG configuration
├── ingest.py           # Document loading
├── retriever.py        # Retrieval logic
├── chain.py            # RAG chain
├── sample_docs/        # Knowledge base
└── chroma_db/          # Vector store

mcp_weather/            # Weather API integration

run_chatbot.py          # Easy launcher
RUN_CHATBOT.bat         # Windows launcher
RUN_CHATBOT.sh          # Linux/Mac launcher

Documentation:
├── README_CHATBOT.md   # This file
├── QUICK_START.md      # 3-step guide
├── FEATURES.md         # Detailed features
├── FEATURES_SUMMARY.md # Technical summary
├── SETUP_CHATBOT.md    # Manual setup
└── TEST_CHATBOT.md     # Testing guide
```

---

## 🎮 Usage Examples

### Example 1: RAG Query
```
You: "What is RAG?"
Bot: "RAG stands for Retrieval Augmented Generation..."
     Sources: doc1.txt, doc2.txt
```

### Example 2: Weather Query
```
You: "What's the weather in Tokyo?"
Bot: "Weather in Tokyo: temperature 18°C, wind 12 km/h"
     Sources: open-meteo
```

### Example 3: Conversation Memory
```
You: "My name is Alice and I love Python"
Bot: "Nice to meet you, Alice! Python is great..."

You: "What programming language do I like?"
Bot: "You mentioned you love Python!"
```

### Example 4: Document Upload
```
1. Click "📎 Upload Document"
2. Select "my_notes.txt"
3. Check ✓ "Re-index documents"
4. Ask: "What's in my notes?"
5. Bot answers from your uploaded file!
```

---

## 🔧 Configuration

### Using OpenAI (Default)

1. Edit `.env`:
```env
CHATBOT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

2. Run chatbot - done!

### Using Ollama (Free, Local)

1. Install Ollama: https://ollama.ai/download

2. Start Ollama:
```bash
ollama serve
```

3. Pull models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

4. Edit `.env`:
```env
CHATBOT_LLM_PROVIDER=ollama
```

5. Run chatbot - no API key needed!

---

## 📚 API Endpoints

### Core Endpoints:

- **`GET /`** - Web UI
- **`GET /docs`** - API documentation
- **`GET /health`** - Health check
- **`POST /chat`** - Send message (with memory)
- **`GET /chat/stream`** - SSE streaming
- **`WebSocket /ws/chat`** - WebSocket chat

### New Endpoints:

- **`POST /upload`** - Upload documents
- **`GET /history/{session_id}`** - Get conversation
- **`DELETE /history/{session_id}`** - Clear history
- **`GET /sessions`** - List all sessions

---

## 🧪 Testing

### Quick Test:

```bash
# Start server
python run_chatbot.py

# In another terminal, test API:
curl http://localhost:8001/health
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Full Test Suite:

See **TEST_CHATBOT.md** for complete testing checklist.

---

## 🎨 UI Features

- ✨ **Gradient theme** - Purple gradient design
- 💬 **Message bubbles** - User vs AI distinction
- 🎭 **Avatars** - Visual indicators for speakers
- ⏳ **Typing indicator** - Animated when bot thinks
- 🔔 **Toast notifications** - Success/error messages
- 📎 **File upload** - Drag & drop support
- 📊 **Status bar** - Connection & session info
- 📜 **Scroll to bottom** - Auto-scroll to latest
- 📱 **Responsive** - Works on mobile

---

## 🔐 Security Notes

- Sessions stored locally in `chatbot/chat_history/`
- No authentication (add if needed for production)
- API keys in `.env` (not committed to git)
- CORS enabled for localhost (restrict for production)

---

## 🚧 Troubleshooting

### Issue: Dependencies not installing
**Solution:** 
```bash
# Close all Python processes
# Delete .venv folder manually
# Run launcher again
python run_chatbot.py
```

### Issue: Port 8001 already in use
**Solution:** 
```bash
# Change port in run_chatbot.py (line ~160)
# Or kill process using port 8001
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall dependencies
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -e .
```

### Issue: Memory not persisting
**Solution:**
```bash
# Check folder permissions
ls -la chatbot/chat_history/
# Should have read/write access
```

### Issue: Can't upload files
**Solution:**
- Check file size (< 10MB recommended)
- Use supported formats: .txt, .md, .pdf
- Check browser console for errors

---

## 📈 Performance

- **Startup time:** ~5 seconds (after first setup)
- **Response time:** 1-3 seconds (depends on LLM)
- **Memory usage:** ~500MB (with ChromaDB)
- **Concurrent users:** 10+ (with uvicorn workers)

### Optimization Tips:

- Use Ollama locally for faster responses
- Increase ChromaDB cache size
- Add Redis for session storage
- Use CDN for static files
- Deploy with Gunicorn + Nginx

---

## 🌟 Features Comparison

| Feature | Included | Details |
|---------|----------|---------|
| RAG | ✅ | ChromaDB + LangChain |
| Weather | ✅ | Open-Meteo API |
| Memory | ✅ | Session-based history |
| Upload | ✅ | File upload via UI |
| History | ✅ | Persistent JSON storage |
| UI | ✅ | Modern gradient design |
| Auth | ❌ | Add if needed |
| Multi-user | ⚠️ | Session-based only |
| Voice I/O | ❌ | Future enhancement |
| Mobile app | ❌ | Future enhancement |

---

## 🎓 Learning Resources

### Documentation:
- **QUICK_START.md** - Get started in 3 steps
- **FEATURES.md** - Detailed feature guide
- **SETUP_CHATBOT.md** - Manual setup instructions
- **TEST_CHATBOT.md** - Testing checklist

### Code Examples:
- `chatbot/api.py` - FastAPI implementation
- `chatbot/graph.py` - LangGraph flow
- `chatbot/memory.py` - Memory management
- `rag/chain.py` - RAG chain construction

---

## 🤝 Contributing

Want to add features?

1. Fork the project
2. Create feature branch
3. Add your feature
4. Test thoroughly
5. Submit pull request

Suggested enhancements:
- User authentication
- Database integration
- Advanced RAG techniques
- Voice input/output
- Multi-language support
- Admin dashboard

---

## 📝 License

This project is provided as-is for learning and development purposes.

---

## 🎉 Credits

Built with:
- **LangChain** - LLM framework
- **LangGraph** - Workflow orchestration
- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **OpenAI/Ollama** - LLM providers
- **Open-Meteo** - Weather API

---

## 📞 Support

**Having issues?**

1. Read **SETUP_CHATBOT.md**
2. Check **TEST_CHATBOT.md**
3. Review error logs
4. Check `.env` configuration
5. Try with Ollama (free, local)

**Everything working?**

Share your success story! 🎊

---

## ⚡ Quick Commands

```bash
# Start chatbot (easy way)
python run_chatbot.py

# Start chatbot (manual)
uvicorn chatbot.api:app --reload --port 8001

# Test health
curl http://localhost:8001/health

# View API docs
# Open: http://localhost:8001/docs

# Run with Ollama
# 1. ollama serve
# 2. Set CHATBOT_LLM_PROVIDER=ollama in .env
# 3. python run_chatbot.py
```

---

**Enjoy your AI chatbot!** 🚀✨

*Built with ❤️ using LangChain, LangGraph, and FastAPI*
