# 🚀 Quick Start - 3 Simple Steps

## Step 1: Run the Launcher

### Windows:
```
Double-click: RUN_CHATBOT.bat
```

### Linux/Mac:
```bash
bash RUN_CHATBOT.sh
```

### Or Python:
```bash
python run_chatbot.py
```

---

## Step 2: Wait for Server to Start

You'll see:
```
✓ Checking Python version...
✓ Checking virtual environment...
✓ Installing dependencies...
✓ Testing chatbot imports...

🚀 Starting Chatbot Server...
📖 Web UI:        http://localhost:8001
📚 API Docs:      http://localhost:8001/docs
```

---

## Step 3: Open Your Browser

Go to: **http://localhost:8001**

---

## 🎉 That's It!

The launcher does everything automatically:
- Creates virtual environment
- Installs all dependencies
- Sets up configuration
- Starts the server

---

## 💡 Try These Commands:

1. **RAG Query:**
   ```
   "What is in the sample docs?"
   ```

2. **Weather Query:**
   ```
   "What's the weather in Paris?"
   ```

3. **Upload a file:**
   - Click "📎 Upload Document"
   - Select a .txt file
   - Check ✓ "Re-index documents"
   - Ask about the file!

4. **Test Memory:**
   ```
   "My name is Alice"
   [then ask]
   "What's my name?"
   ```

---

## 🔧 Troubleshooting

### If it doesn't work:

1. **Close ALL Python processes and terminals**
2. **Delete the `.venv` folder manually**
3. **Run the launcher again**

### Still having issues?

Read: **SETUP_CHATBOT.md** for detailed instructions

---

## 🎯 Features Available:

✅ RAG (Retrieval Augmented Generation)
✅ Weather queries (Open-Meteo API)
✅ Conversation memory
✅ Document upload
✅ Chat history persistence
✅ Beautiful modern UI
✅ Session management

---

## ⚡ Pro Tip:

Use **Ollama** for completely free local LLM:

1. Install: https://ollama.ai/download
2. Run: `ollama serve`
3. Pull model: `ollama pull llama3.2`
4. Edit `.env`: `CHATBOT_LLM_PROVIDER=ollama`

No API key needed! 🎉
