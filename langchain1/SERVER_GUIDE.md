# 🚀 Production Server Guide

## Quick Start

### Option 1: Use the Deployment Helper (Recommended)
```bash
python langchain1/deploy_local.py
```
This will:
- ✅ Check all dependencies
- ✅ Validate configuration
- ✅ Check integrations
- ✅ Start the server with proper settings

### Option 2: Manual Start
```bash
uvicorn langchain1.production_server:app --reload --port 8002
```

---

## 🔧 Server Endpoints

Once the server is running, access these URLs:

### 📖 Documentation
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

### ❤️ Health & Monitoring
- **Health Check**: http://localhost:8002/health
- **Metrics**: http://localhost:8002/metrics

### 💬 Chat API (REST)

#### Send a Message
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What can you do?",
    "session_id": "my-session"
  }'
```

#### Get Conversation History
```bash
curl http://localhost:8002/chat/my-session/history
```

#### Clear Session
```bash
curl -X DELETE http://localhost:8002/chat/my-session
```

#### Get All Sessions
```bash
curl http://localhost:8002/sessions
```

### 🔌 WebSocket (Real-time Streaming)

Connect to: `ws://localhost:8002/ws/chat/{session_id}`

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8002/ws/chat/my-session');

ws.onopen = () => {
    ws.send(JSON.stringify({
        message: "Hello!",
        stream: true
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

**Python Example:**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8002/ws/chat/my-session"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "message": "Hello!",
            "stream": true
        }))
        
        # Receive streaming response
        async for message in websocket:
            data = json.loads(message)
            print(data)

asyncio.run(chat())
```

---

## 🧪 Testing the Server

### Option 1: Use the Test Script (Recommended)
```bash
# In a new terminal (keep server running)
python langchain1/test_server.py
```

This will test:
- ✅ Health check
- ✅ Send message
- ✅ Memory (conversation context)
- ✅ RAG integration
- ✅ Get history
- ✅ Get sessions
- ✅ Metrics
- ✅ Clear session

### Option 2: Manual Testing with cURL

**1. Health Check:**
```bash
curl http://localhost:8002/health
```

**2. Send a Message:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "session_id": "test1"}'
```

**3. Test Memory:**
```bash
# First message
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My name is Alice", "session_id": "test2"}'

# Follow-up (should remember)
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my name?", "session_id": "test2"}'
```

**4. Get History:**
```bash
curl http://localhost:8002/chat/test2/history
```

**5. View All Sessions:**
```bash
curl http://localhost:8002/sessions
```

### Option 3: Use the Interactive API Docs
Visit http://localhost:8002/docs and try the endpoints interactively!

---

## 📊 Server Features

### Memory Management
The server includes **4 memory strategies**:
- **Buffer Memory**: Keeps all messages
- **Summary Memory**: Summarizes old messages
- **Entity Memory**: Tracks people, places, facts
- **Window Memory**: Keeps last N messages

Configure in the request:
```json
{
  "message": "Hello",
  "session_id": "my-session",
  "memory_type": "entity"
}
```

### ReAct Agent
The server can use **ReAct reasoning** for complex queries:
```json
{
  "message": "What is 25 * 47 + 100?",
  "session_id": "my-session",
  "use_react": true
}
```

### RAG Integration
Automatically searches your documents:
```json
{
  "message": "What is RAG?",
  "session_id": "my-session",
  "top_k": 3
}
```

### Tools Available
- 🧮 **Calculator**: Math calculations
- 📚 **RAG Search**: Document retrieval
- 🌤️ **Weather**: Weather information
- 🐍 **Python REPL**: Code execution (disabled by default for security)
- 📧 **Email**: Send emails (if configured)
- 💾 **Database**: Query databases (if configured)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in `langchain1/`:
```bash
cp langchain1/.env.example langchain1/.env
```

Edit `.env`:
```env
# LLM Provider
OPENAI_API_KEY=your-key-here

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8002
DEBUG=false

# Memory
MAX_MEMORY_TOKENS=2000
WINDOW_SIZE=10

# RAG
RAG_TOP_K=3

# Tools
ENABLE_CALCULATOR=true
ENABLE_PYTHON_REPL=false  # Security risk
ENABLE_RAG=true
ENABLE_WEATHER=true
```

### Command Line Options

**Change port:**
```bash
uvicorn langchain1.production_server:app --port 8003
```

**Disable auto-reload:**
```bash
uvicorn langchain1.production_server:app --port 8002 --no-reload
```

**Multiple workers (production):**
```bash
uvicorn langchain1.production_server:app --port 8002 --workers 4
```

**Bind to specific host:**
```bash
uvicorn langchain1.production_server:app --host 127.0.0.1 --port 8002
```

---

## 🐛 Troubleshooting

### Server won't start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r langchain1/requirements.txt
```

**Problem:** `Address already in use`
```bash
# Solution: Change port or kill existing process
uvicorn langchain1.production_server:app --port 8003
```

**Problem:** `ImportError: cannot import name 'production_server'`
```bash
# Solution: Run from project root
cd /path/to/project
uvicorn langchain1.production_server:app --reload
```

### API errors

**Problem:** `500 Internal Server Error`
- Check server logs in terminal
- Verify `.env` configuration
- Check if RAG/Weather integrations are available

**Problem:** `Session not found`
- Sessions are in-memory by default
- Use Redis for persistent sessions (see DEPLOYMENT_GUIDE.md)

**Problem:** `Rate limit exceeded`
- Default: 100 requests/minute
- Configure in `.env`: `RATE_LIMIT_REQUESTS=200`

### Memory not working

**Problem:** Bot doesn't remember previous messages
- Check `session_id` is the same for both requests
- Verify memory type is set correctly
- Check server logs for errors

---

## 📈 Monitoring

### Metrics Endpoint
Visit http://localhost:8002/metrics for Prometheus metrics:
- Request count
- Response times
- Error rates
- Active sessions

### Logs
The server logs to stdout. View with:
```bash
# If using deployment helper
# Logs appear in terminal

# If running in background
uvicorn langchain1.production_server:app --log-level info
```

### Health Monitoring
Set up automated health checks:
```bash
# Check every 30 seconds
watch -n 30 curl http://localhost:8002/health
```

---

## 🚀 Next Steps

### Development
1. ✅ Start server locally
2. ✅ Test with test_server.py
3. ✅ Try API docs at /docs
4. ✅ Create custom tools (see CUSTOM_TOOLS_GUIDE.md)

### Production
1. ✅ Configure .env properly
2. ✅ Set up Redis for sessions
3. ✅ Set up PostgreSQL for persistent storage
4. ✅ Use Docker (see DEPLOYMENT_GUIDE.md)
5. ✅ Set up monitoring (Sentry, Prometheus)
6. ✅ Configure SSL/TLS
7. ✅ Set up load balancer

---

## 📚 Related Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment guide
- [CUSTOM_TOOLS_GUIDE.md](CUSTOM_TOOLS_GUIDE.md) - Creating tools
- [MEMORY_REACT_GUIDE.md](MEMORY_REACT_GUIDE.md) - Memory & ReAct patterns
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Integration details

---

## 🎉 Quick Demo

```bash
# Terminal 1: Start server
python langchain1/deploy_local.py

# Terminal 2: Test it
python langchain1/test_server.py

# Or use curl
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! My name is Alice and I love Python.", "session_id": "demo"}'

curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do I love?", "session_id": "demo"}'
```

Enjoy your production server! 🚀
