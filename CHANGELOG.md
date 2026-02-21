# 📝 Changelog

## Version 0.2.0 - Enhanced Features (Current)

### 🎉 Major Features Added

#### 1. Conversation Memory System
- **New file:** `chatbot/memory.py`
- Session-based conversation tracking
- Context-aware responses (remembers last 5 messages)
- Persistent storage in `chatbot/chat_history/`
- Message timestamps and metadata

#### 2. Document Upload Feature
- **New endpoint:** `POST /upload`
- Drag & drop file upload in UI
- Support for `.txt`, `.md`, `.pdf` files
- Automatic indexing into RAG system
- Uploaded files stored in `chatbot/uploads/`

#### 3. Chat History Management
- **New endpoint:** `GET /history/{session_id}`
- **New endpoint:** `DELETE /history/{session_id}`
- **New endpoint:** `GET /sessions`
- Export conversations as JSON
- Load previous sessions automatically
- Session persistence across refreshes

#### 4. Modern Enhanced UI
- **Updated:** `chatbot/static/index.html`
- Beautiful purple gradient theme
- Message avatars (User vs AI)
- Typing indicator animation
- Toast notifications for actions
- Source citations displayed
- Status bar with session info
- Smooth animations and transitions
- Responsive mobile-friendly layout
- File upload button integrated

#### 5. Easy Launcher System
- **New file:** `run_chatbot.py`
- **New file:** `RUN_CHATBOT.bat` (Windows)
- **New file:** `RUN_CHATBOT.sh` (Linux/Mac)
- Auto-detect Python version
- Auto-create virtual environment
- Auto-install dependencies
- Auto-configure environment
- One-click startup experience

### 🔧 Technical Changes

#### API Updates
- `ChatRequest` model: Added `session_id` field
- `ChatResponse` model: Added `session_id` field
- `ChatState` TypedDict: Added `session_id` and `chat_history` fields
- CORS middleware added for web UI support

#### Function Signatures Changed
- `build_rag_chain()`: Added `chat_history` parameter
- `handle_rag()`: Now passes conversation context to chain

#### Dependencies
- No new dependencies (uses existing packages)
- All features work with current `pyproject.toml`

### 📚 Documentation

#### New Documentation Files
- `🚀_START_HERE.md` - Quick start guide (read first!)
- `QUICK_START.md` - 3-step getting started
- `README_CHATBOT.md` - Complete project README
- `FEATURES.md` - Detailed feature documentation
- `FEATURES_SUMMARY.md` - Technical feature summary
- `SETUP_CHATBOT.md` - Manual setup instructions
- `TEST_CHATBOT.md` - Testing checklist
- `CHANGELOG.md` - This file

#### Updated Files
- `chatbot/api.py` - Added new endpoints and memory integration
- `chatbot/graph.py` - Added memory state management
- `rag/chain.py` - Added conversation history support
- `chatbot/static/index.html` - Complete UI overhaul

### 🐛 Bug Fixes
- Fixed virtual environment corruption issues with auto-reinstall
- Improved error handling for missing dependencies
- Better session management to prevent data loss

### ⚡ Performance Improvements
- Session data cached in memory for faster access
- Lazy loading of conversation history
- Optimized message persistence

---

## Version 0.1.0 - Initial Release

### Features
- Basic RAG pipeline with ChromaDB
- Weather integration (Open-Meteo API)
- LangGraph flow orchestration
- REST API with FastAPI
- WebSocket support
- Server-Sent Events (SSE) streaming
- Basic HTML UI
- OpenAI + Ollama LLM support
- Environment configuration (.env)

### Components
- `chatbot/api.py` - FastAPI server
- `chatbot/graph.py` - LangGraph orchestration
- `chatbot/llm_provider.py` - LLM abstraction
- `rag/` - RAG pipeline components
- `mcp_weather/` - Weather integration
- `chatbot/static/index.html` - Basic UI

---

## Migration Guide: 0.1.0 → 0.2.0

### For Users
**No action needed!** Just run the new launcher:
```bash
python run_chatbot.py
```

### For Developers

#### API Changes
**Chat endpoint now returns session_id:**
```python
# Before
response = {"answer": "...", "sources": [...]}

# After
response = {"answer": "...", "sources": [...], "session_id": "uuid"}
```

**Chat request accepts optional session_id:**
```python
# Before
{"message": "Hello"}

# After (optional)
{"message": "Hello", "session_id": "my-session"}
```

#### Code Changes
If you were importing functions:

```python
# build_rag_chain signature changed
# Before
chain = build_rag_chain(retriever, llm)

# After
chain = build_rag_chain(retriever, llm, chat_history="...")
```

#### Storage Changes
New directories created:
- `chatbot/chat_history/` - Conversation storage
- `chatbot/uploads/` - User uploaded files

---

## Roadmap

### Version 0.3.0 (Future)
- [ ] User authentication
- [ ] Multi-user support
- [ ] Advanced RAG (reranking, hybrid search)
- [ ] Voice input/output
- [ ] Admin dashboard
- [ ] Docker deployment
- [ ] Cloud hosting guide

### Version 0.4.0 (Future)
- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Custom tool integration
- [ ] Advanced analytics
- [ ] Plugin system
- [ ] Multi-language support

---

## Breaking Changes

### Version 0.2.0
**None!** Fully backwards compatible with 0.1.0

All old API calls still work. New features are additive.

---

## Deprecations

### Version 0.2.0
**None.** All features from 0.1.0 are still supported.

---

## Known Issues

### Version 0.2.0
1. **Virtual environment corruption** on Windows with locked files
   - **Workaround:** Close all Python processes, delete .venv, re-run launcher
   
2. **Large file uploads** may timeout
   - **Workaround:** Keep uploads under 10MB, use smaller chunks

3. **Browser back button** creates new session
   - **Workaround:** Use the UI's clear button instead

4. **Memory uses disk storage** (not database)
   - **Future:** Will add optional database backend

---

## Contributors

- Development team
- LangChain community
- FastAPI community

---

## Acknowledgments

Built with:
- LangChain & LangGraph
- FastAPI & Uvicorn
- ChromaDB
- OpenAI / Ollama
- Open-Meteo API

---

*For detailed feature documentation, see FEATURES.md*
*For setup instructions, see SETUP_CHATBOT.md*
*For quick start, see QUICK_START.md*
