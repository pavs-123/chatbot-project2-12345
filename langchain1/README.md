# 🚀 LangChain1 - Complete LangGraph System

**Production-ready Memory + ReAct Agent with RAG & Weather Integration**

> 🎯 **New here?** Run `python langchain1/start_here.py` for an interactive guide!  
> 📖 **Want overview?** Read [MASTER_GUIDE.md](MASTER_GUIDE.md) for the complete picture!

This comprehensive system demonstrates **LangGraph** with **Memory**, **ReAct reasoning**, **RAG**, and **Weather** integration using **SystemMessage**, **HumanMessage**, and **AIMessage**.

## 📁 Contents

### 🎓 Learning Examples
- **`langgraph_messages.ipynb`** - Interactive Jupyter notebook with basic LangGraph examples
- **`memory_notebook.ipynb`** - Memory strategies tutorial (buffer, summary, entity, window)
- **`react_notebook.ipynb`** - ReAct agent tutorial with tools
- **`run_example.py`** - Standalone Python script you can run directly (no Jupyter needed)
- **`graph_visualization.md`** - Detailed graph visualization with Mermaid diagrams

### 🔗 **Integrated System**
- **`integrated_chatbot.py`** - Full integration with existing chatbot + RAG system
- **`integrated_notebook.ipynb`** - Interactive notebook demonstrating the integrated system
- **`integrated_api.py`** - FastAPI server with session-based chat and message history

### 🧠 **Advanced Features** (New!)
- **`memory_chatbot.py`** - Chatbot with multiple memory strategies (buffer, summary, entity, window)
- **`react_agent.py`** - ReAct agent (Reasoning + Acting) with tools
- **`advanced_agent.py`** - Combined Memory + ReAct + RAG + Weather (most powerful!)
- **`MEMORY_REACT_GUIDE.md`** - Complete guide for memory and ReAct patterns

### 📚 **Documentation**
- **`README.md`** - This file (complete guide)
- **`QUICK_START.md`** - 5-minute getting started guide ⚡
- **`EXAMPLES.md`** - Practical examples and use cases
- **`INTEGRATION_GUIDE.md`** - Technical integration details
- **`MEMORY_REACT_GUIDE.md`** - Memory & ReAct patterns
- **`SUMMARY.md`** - Quick reference

## 🚀 Quick Start

> **⚡ New to LangGraph?** Check out [QUICK_START.md](QUICK_START.md) for a 5-minute getting started guide!

### Option 1: Run the Basic Example (Easiest)
```bash
python langchain1/run_example.py
```
This will run two examples and show you how messages flow through the graph.

### Option 2: Run the Integrated Chatbot (Real-world Example)
```bash
# Ask a RAG question
python langchain1/integrated_chatbot.py --query "What is RAG?" --visualize

# Ask a weather question
python langchain1/integrated_chatbot.py --query "What's the weather in London?"
```

### Option 2a: Memory-Enabled Chatbot ⭐ (NEW!)
```bash
# Start a conversation with memory
python langchain1/memory_chatbot.py --query "My name is Alice" --memory-type entity

# Continue the conversation (it remembers you!)
python langchain1/memory_chatbot.py --query "What's my name?" --session-id <id> --memory-type entity
```

### Option 2b: ReAct Agent ⭐ (NEW!)
```bash
# Math calculation with reasoning
python langchain1/react_agent.py --query "What is 25 * 47 + 100?"

# Multi-step task with tools
python langchain1/react_agent.py --query "Get weather in Paris and multiply temperature by 2"
```

### Option 2c: Advanced Agent (Memory + ReAct) 🚀 (NEW!)
```bash
# It combines memory AND reasoning!
python langchain1/advanced_agent.py --query "My name is Bob and I live in Tokyo"
python langchain1/advanced_agent.py --query "What's the weather where I live?" --session-id <id>
```

### Option 3: Start the Production Server ⭐ (RECOMMENDED)
```bash
# Use the deployment helper (checks everything)
python langchain1/deploy_local.py

# Or start manually
uvicorn langchain1.production_server:app --reload --port 8002
```
Then visit:
- **API Docs**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health
- **Metrics**: http://localhost:8002/metrics

**Test the server:**
```bash
python langchain1/test_server.py
```

See [SERVER_GUIDE.md](SERVER_GUIDE.md) for complete server documentation.

### Option 4: Use the Jupyter Notebook (Interactive)

1. **Install ipykernel** (already done ✅):
   ```bash
   pip install ipykernel
   ```

2. **Open the notebook**:
   ```bash
   jupyter notebook langchain1/langgraph_messages.ipynb
   ```
   Or open it in VS Code with Jupyter extension

3. **Run all cells** to see:
   - How to define graph state with messages
   - How to create nodes that process SystemMessage and HumanMessage
   - How to connect nodes with conditional edges
   - Multiple visualization methods (ASCII, Mermaid, PNG)
   - How messages flow through the graph

## 📚 What You'll Learn

- ✅ Using `SystemMessage` to set context for the AI
- ✅ Using `HumanMessage` for user input
- ✅ Using `AIMessage` for AI responses
- ✅ Connecting nodes with edges in LangGraph
- ✅ Routing messages through conditional edges
- ✅ Building multi-step conversation flows
- ✅ Visualizing graph structure (ASCII, Mermaid, PNG)
- ✅ Managing message state with `add_messages` annotation

## 🔧 Requirements

All dependencies are already in your `pyproject.toml`:
- `langgraph>=1.0.7`
- `langchain>=1.2.7`
- `langchain-core` (included with langchain)
- `ipykernel` (for running notebooks)

## 💡 Key Concepts

### Graph Structure
```
initialize (SystemMessage) 
    ↓
process (HumanMessage)
    ↓
finalize (AIMessage)
    ↓
END
```

### Message Flow
1. **Initialize Node**: Adds SystemMessage to set context
2. **Process Node**: Processes HumanMessage from user
3. **Finalize Node**: Adds final AIMessage response
4. **Routing**: Uses conditional edges to connect nodes based on state

## 🎨 Visualization

The notebook includes **4 visualization methods**:

1. **ASCII Diagram** - Simple text representation
2. **Graph Nodes & Edges** - Programmatic inspection
3. **Mermaid Diagram** - Copy to [mermaid.live](https://mermaid.live) for interactive rendering
4. **PNG Image** - Direct visualization (if dependencies available)

See `graph_visualization.md` for a detailed Mermaid diagram you can view online!

## 🧪 Testing

Both the notebook and Python script have been designed to work out of the box. Simply run them to see:

- Graph execution with logging
- Message flow through nodes
- Conditional routing in action
- Final message history

## 🌟 Features Overview

### **Integrated System** (`integrated_chatbot.py` and `integrated_api.py`)
- ✅ **Message Type Tracking**: Full SystemMessage, HumanMessage, AIMessage history
- ✅ **RAG Integration**: Uses your existing `rag/` system
- ✅ **Weather Integration**: Uses your existing `mcp_weather/` system
- ✅ **Intent Detection**: Automatically routes to RAG or Weather
- ✅ **Session Management**: Track conversations across multiple messages
- ✅ **WebSocket Support**: Real-time streaming chat
- ✅ **Graph Visualization**: ASCII, Mermaid, and PNG exports

### **Memory System** ⭐ (`memory_chatbot.py`)
- ✅ **Buffer Memory**: Store full conversation history
- ✅ **Summary Memory**: Automatically summarize old conversations
- ✅ **Entity Memory**: Track people, places, facts mentioned
- ✅ **Window Memory**: Keep only last N messages
- ✅ **Persistent Storage**: Sessions saved to disk

### **ReAct Agent** 🤖 (`react_agent.py`)
- ✅ **Reasoning Pattern**: Thought → Action → Observation loop
- ✅ **Calculator Tool**: Perform math calculations
- ✅ **Search Tool**: Query knowledge base (RAG)
- ✅ **Weather Tool**: Get weather information
- ✅ **Python REPL**: Execute Python code safely
- ✅ **Multi-step Tasks**: Handle complex queries automatically

### **Advanced Agent** 🚀 (`advanced_agent.py`)
- ✅ **Memory + ReAct Combined**: Best of both worlds!
- ✅ **Auto Mode Detection**: Automatically chooses simple or reasoning mode
- ✅ **Entity Tracking**: Remembers context across reasoning steps
- ✅ **All Tools Available**: Calculator, RAG, Weather, Python
- ✅ **Session Persistence**: Continue conversations later

## 📖 Next Steps

After understanding the basics, you can:

1. ✅ **Use the integrated chatbot** - Already connected to your RAG and Weather systems!
2. Add more complex routing logic
3. Build multi-agent systems
4. Extend the API with custom endpoints
5. Deploy to production with session persistence (Redis/DB)

## 🧪 API Usage Examples

### Using cURL
```bash
# Send a message
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?"}'

# Get message history
curl http://localhost:8002/chat/{session_id}/history

# Visualize the graph
curl http://localhost:8002/visualize
```

### Using Python
```python
import requests

# Chat with the bot
response = requests.post("http://localhost:8002/chat", json={
    "message": "What's the weather in Paris?",
    "top_k": 4
})
print(response.json())
```

Enjoy exploring LangGraph! 🎉
