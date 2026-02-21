# 🧪 Chatbot Testing Guide

## Quick Test

Run the chatbot and test all features:

```bash
python run_chatbot.py
```

Then open http://localhost:8001 and try these tests:

---

## ✅ Test Checklist

### 1. Basic Startup Test
- [ ] Server starts without errors
- [ ] Web UI loads at http://localhost:8001
- [ ] Welcome message appears
- [ ] Session ID is displayed

### 2. RAG Query Test
```
Type: "What is in the sample docs?"
Expected: Answer based on files in rag/sample_docs/
```

### 3. Weather Query Test
```
Type: "What's the weather in London?"
Expected: Temperature, wind speed, weather code
```

### 4. Conversation Memory Test
```
Step 1: "My favorite color is blue"
Step 2: "What's my favorite color?"
Expected: Bot remembers "blue"
```

### 5. Document Upload Test
- [ ] Click "📎 Upload Document"
- [ ] Select a .txt or .md file
- [ ] Check ✓ "Re-index documents"
- [ ] Ask question about the uploaded file
- [ ] Bot answers from the new document

### 6. History Features Test
- [ ] Click "📜 History" - see session info
- [ ] Click "💾 Save" - download JSON file
- [ ] Click "🗑️ Clear" - chat clears
- [ ] Refresh page - history should reload

### 7. UI Features Test
- [ ] Typing indicator appears when bot thinks
- [ ] Messages have avatars (You vs AI)
- [ ] Sources shown with RAG answers
- [ ] Toast notifications on upload
- [ ] Smooth animations
- [ ] Scrolling works properly

---

## 🐛 Known Issues to Check

1. **Environment corruption** - Fixed by run_chatbot.py
2. **Import errors** - Launcher installs dependencies
3. **Port conflicts** - Change port in run_chatbot.py if needed

---

## 📊 Manual API Tests

### Test Health Endpoint
```bash
curl http://localhost:8001/health
# Expected: {"status": "ok"}
```

### Test Chat API
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Test Upload API
```bash
curl -X POST http://localhost:8001/upload \
  -F "file=@test.txt"
```

### Test History API
```bash
curl http://localhost:8001/sessions
# Expected: List of session IDs
```

---

## ✨ Success Criteria

✅ All features work without errors
✅ Memory persists across messages
✅ Documents upload successfully
✅ UI is responsive and smooth
✅ Server starts with one command
✅ No manual configuration needed

---

## 🚀 Ready to Use!

If all tests pass, your chatbot is ready for:
- Personal use
- Team demos
- Production deployment
- Feature extensions
