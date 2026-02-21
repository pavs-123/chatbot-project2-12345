# 🚀 Start the Server - Quick Guide

## ⚡ Fastest Way (Recommended)

```bash
python langchain1/deploy_local.py
```

This will:
1. ✅ Check all dependencies
2. ✅ Validate configuration
3. ✅ Start the server
4. ✅ Show you all available endpoints

---

## 📋 Step-by-Step Instructions

### Step 1: Check Dependencies
```bash
pip install -r langchain1/requirements.txt
```

### Step 2: Configure Environment (Optional)
```bash
# Copy example config
cp langchain1/.env.example langchain1/.env

# Edit and add your API keys
# nano langchain1/.env
# or
# code langchain1/.env
```

### Step 3: Start Server
```bash
python langchain1/deploy_local.py
```

**Or manually:**
```bash
uvicorn langchain1.production_server:app --reload --port 8002
```

### Step 4: Test It
**In a new terminal:**
```bash
python langchain1/test_server.py
```

---

## 🎯 What You'll See

When the server starts, you'll see:
```
🚀 Starting server... (Press Ctrl+C to stop)
================================================================================

INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Application startup complete.
```

### Available URLs:
- 📖 **API Docs**: http://localhost:8002/docs
- 📚 **Alternative Docs**: http://localhost:8002/redoc  
- ❤️ **Health Check**: http://localhost:8002/health
- 📊 **Metrics**: http://localhost:8002/metrics

---

## 🧪 Quick Test

### Test 1: Health Check
```bash
curl http://localhost:8002/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-20T22:00:00"
}
```

### Test 2: Send a Message
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?", "session_id": "test1"}'
```

### Test 3: Test Memory
```bash
# First message
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My name is Alice", "session_id": "memory-test"}'

# Second message (should remember)
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my name?", "session_id": "memory-test"}'
```

---

## 🎨 Using the Interactive API Docs

1. Open http://localhost:8002/docs in your browser
2. Click on any endpoint (e.g., "POST /chat")
3. Click "Try it out"
4. Enter your request:
   ```json
   {
     "message": "Hello!",
     "session_id": "web-test"
   }
   ```
5. Click "Execute"
6. See the response!

---

## 🔌 WebSocket Example

Connect to streaming chat:

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8002/ws/chat/my-session');

ws.onopen = () => {
    console.log('Connected!');
    ws.send(JSON.stringify({
        message: "Tell me a story",
        stream: true
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Chunk:', data.chunk);
};
```

**Python:**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8002/ws/chat/my-session"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "message": "Hello!",
            "stream": True
        }))
        
        async for msg in ws:
            data = json.loads(msg)
            print(data['chunk'], end='', flush=True)

asyncio.run(chat())
```

---

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## 📚 Next Steps

- ✅ Read [SERVER_GUIDE.md](SERVER_GUIDE.md) for complete documentation
- ✅ Try [test_server.py](test_server.py) for automated testing
- ✅ Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment
- ✅ Customize with [CUSTOM_TOOLS_GUIDE.md](CUSTOM_TOOLS_GUIDE.md)

---

## 🆘 Troubleshooting

**Server won't start?**
```bash
# Check if port is in use
lsof -i :8002  # Mac/Linux
netstat -ano | findstr :8002  # Windows

# Use different port
uvicorn langchain1.production_server:app --port 8003
```

**Missing dependencies?**
```bash
pip install -r langchain1/requirements.txt
```

**Import errors?**
```bash
# Make sure you're in the project root
cd /path/to/your/project
python langchain1/deploy_local.py
```

---

Happy deploying! 🎉
