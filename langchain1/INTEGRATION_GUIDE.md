# Integration Guide: LangGraph with Chatbot & RAG

This guide explains how the `langchain1/` LangGraph implementation integrates with your existing `chatbot/` and `rag/` systems.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query (HumanMessage)                 │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
           ┌───────────────────────┐
           │   detect_intent_node   │
           │  (SystemMessage added) │
           └───────────┬───────────┘
                       ↓
              ┌────────┴────────┐
              │   Router Logic   │
              └────────┬────────┘
                       ↓
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌────────────────┐          ┌────────────────┐
│  weather_node  │          │    rag_node    │
│  (uses mcp_    │          │  (uses rag/    │
│   weather)     │          │   system)      │
└────────┬───────┘          └────────┬───────┘
         │                           │
         └─────────────┬─────────────┘
                       ↓
              ┌────────────────┐
              │ finalize_node   │
              │ (AIMessage)     │
              └────────┬────────┘
                       ↓
              ┌────────────────┐
              │   END          │
              └────────────────┘
```

## 🔌 Integration Points

### 1. **Message Types** (LangChain Core)

The integration uses proper message types throughout:

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# User input
HumanMessage(content="What is RAG?")

# System context
SystemMessage(content="Intent detected: RAG query. Searching knowledge base...")

# AI response
AIMessage(content="RAG stands for Retrieval-Augmented Generation...")
```

### 2. **RAG System Integration** (`rag/`)

The `rag_node` function uses your existing RAG components:

```python
from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain

# Inside rag_node
cfg = RAGConfig()
embeddings = get_embeddings()  # From chatbot.llm_provider
vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, reingest, embeddings)
retriever = get_retriever(vectorstore, k=top_k)
llm = get_llm()  # From chatbot.llm_provider
chain = build_rag_chain(retriever, llm)
answer = chain.invoke(query)
```

**Files Used:**
- `rag/config.py` - Configuration
- `rag/ingest.py` - Vector store creation
- `rag/retriever.py` - Document retrieval
- `rag/chain.py` - RAG chain building

### 3. **Weather Integration** (`mcp_weather/`)

The `weather_node` uses your MCP Weather helpers:

```python
from mcp_weather import helpers as weather_helpers
import anyio

# Inside weather_node
async def _call(city: str):
    info = await weather_helpers.geocode_city(city)
    data = await weather_helpers.fetch_weather(info["latitude"], info["longitude"])
    return data

result = anyio.run(_call, city)
```

**Files Used:**
- `mcp_weather/helpers.py` - Geocoding and weather fetching
- Uses `anyio` to run async functions in sync context

### 4. **LLM Provider Integration** (`chatbot/llm_provider.py`)

Supports both OpenAI and Ollama:

```python
from chatbot.llm_provider import get_llm, get_embeddings

# Get LLM (respects CHATBOT_LLM_PROVIDER env var)
llm = get_llm()  # Returns ChatOpenAI or ChatOllama

# Get embeddings
embeddings = get_embeddings()  # Returns OpenAIEmbeddings or OllamaEmbeddings
```

**Environment Variables:**
- `CHATBOT_LLM_PROVIDER` - "openai" (default) or "ollama"
- `OPENAI_API_KEY` - Required for OpenAI
- `OLLAMA_MODEL` - Model for Ollama (default: llama3.2)
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)

## 📊 State Management

### ConversationState

The graph uses a typed state dictionary:

```python
class ConversationState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Message history
    route: str                    # "weather" | "rag"
    user_query: str               # Original query text
    answer: str                   # Final answer
    sources: List[str]            # Source documents/APIs
    reingest: bool                # Re-build vector DB?
    top_k: int                    # Number of docs to retrieve
```

### Message History Tracking

Messages accumulate using the `operator.add` annotation:

```python
messages: Annotated[Sequence[BaseMessage], operator.add]
```

This means each node can add new messages, and they're automatically appended to the history.

## 🔄 Comparison with Original Chatbot

### Original (`chatbot/graph.py`)

```python
class ChatState(TypedDict, total=False):
    message: str      # Just the text
    route: str
    answer: str
    sources: List[str]
```

**Limitations:**
- No message history tracking
- No message type distinction
- Single turn only

### Integrated (`langchain1/integrated_chatbot.py`)

```python
class ConversationState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Full history
    route: str
    user_query: str
    answer: str
    sources: List[str]
    reingest: bool
    top_k: int
```

**Improvements:**
- ✅ Full message history (SystemMessage, HumanMessage, AIMessage)
- ✅ Multi-turn conversations
- ✅ Message type tracking
- ✅ Better debugging and visualization

## 🚀 Usage Patterns

### Pattern 1: Command-Line Chat

```bash
python langchain1/integrated_chatbot.py --query "What is RAG?" --visualize
```

### Pattern 2: API Server (Session-based)

```python
import requests

# First message (creates session)
resp1 = requests.post("http://localhost:8002/chat", json={
    "message": "What is RAG?"
})
session_id = resp1.json()["session_id"]

# Follow-up message (continues conversation)
resp2 = requests.post("http://localhost:8002/chat", json={
    "message": "Can you explain more?",
    "session_id": session_id
})

# Get full message history
history = requests.get(f"http://localhost:8002/chat/{session_id}/history")
print(history.json())
```

### Pattern 3: Direct Graph Invocation

```python
from langchain1.integrated_chatbot import build_integrated_chatbot, ConversationState
from langchain_core.messages import HumanMessage

chatbot = build_integrated_chatbot()

# First query
state1 = ConversationState(
    messages=[HumanMessage(content="What is RAG?")],
    route="",
    user_query="What is RAG?",
    answer="",
    sources=[],
    reingest=False,
    top_k=4,
)
result1 = chatbot.invoke(state1)

# Follow-up (with message history)
state2 = result1.copy()
state2["messages"].append(HumanMessage(content="Tell me more"))
state2["user_query"] = "Tell me more"
result2 = chatbot.invoke(state2)

# Print full conversation
for msg in result2["messages"]:
    print(f"[{type(msg).__name__}] {msg.content}")
```

## 🧪 Testing Integration

### Test RAG Integration

```bash
# Make sure you have documents in rag/sample_docs/
python langchain1/integrated_chatbot.py --query "What is in the documents?"
```

### Test Weather Integration

```bash
python langchain1/integrated_chatbot.py --query "What's the weather in Tokyo?"
```

### Test API

```bash
# Terminal 1: Start server
uvicorn langchain1.integrated_api:app --reload --port 8002

# Terminal 2: Test
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?"}'
```

## 🔧 Extending the Integration

### Add a New Node

1. Define the node function:
```python
def my_custom_node(state: ConversationState) -> ConversationState:
    # Add system message
    sys_msg = SystemMessage(content="Processing custom logic...")
    
    # Your logic here
    result = custom_processing(state["user_query"])
    
    # Add AI message
    ai_msg = AIMessage(content=result)
    
    return {
        "messages": [sys_msg, ai_msg],
        "answer": result,
        # ... other state fields
    }
```

2. Add to graph:
```python
graph.add_node("custom", my_custom_node)
graph.add_edge("detect_intent", "custom")
```

### Add a New Route

1. Update the router:
```python
def detect_intent_node(state: ConversationState) -> ConversationState:
    msg = state["user_query"].lower()
    
    if "custom" in msg:
        route = "custom"
        system_msg = SystemMessage(content="Routing to custom handler...")
    elif "weather" in msg:
        route = "weather"
        # ...
    else:
        route = "rag"
        # ...
```

2. Update conditional edges:
```python
graph.add_conditional_edges(
    "detect_intent",
    route_by_intent,
    {
        "weather": "weather",
        "rag": "rag",
        "custom": "custom",  # New route
    }
)
```

## 📈 Monitoring & Debugging

### View Message Flow

```python
from langchain1.integrated_chatbot import print_message_history

result = chatbot.invoke(state)
print_message_history(result)
```

Output:
```
============================================================
MESSAGE HISTORY
============================================================

1. [HumanMessage]
   What is RAG?

2. [SystemMessage]
   Intent detected: RAG query. I will search my knowledge base...

3. [SystemMessage]
   Processing RAG query. Retrieving relevant documents...

4. [AIMessage]
   RAG stands for Retrieval-Augmented Generation...

5. [SystemMessage]
   Response completed. Sources used: doc1.txt, doc2.txt

============================================================
Final Answer: RAG stands for Retrieval-Augmented Generation...
Sources: doc1.txt, doc2.txt
============================================================
```

### Graph Visualization

```bash
python langchain1/integrated_chatbot.py --query "test" --visualize
```

### API Session Monitoring

```bash
# List all sessions
curl http://localhost:8002/sessions

# Get specific session history
curl http://localhost:8002/chat/{session_id}/history
```

## 🎯 Best Practices

1. **Message Types**: Always use proper message types (SystemMessage, HumanMessage, AIMessage)
2. **State Immutability**: Return new state dicts from nodes, don't mutate in place
3. **Error Handling**: Wrap external calls (RAG, Weather) in try/except
4. **Session Cleanup**: Implement session expiration for production APIs
5. **Logging**: Add logging to track message flow and debugging

## 📚 References

- **Original Chatbot**: `chatbot/graph.py`
- **Original RAG**: `rag/chain.py`
- **LLM Provider**: `chatbot/llm_provider.py`
- **Weather Helpers**: `mcp_weather/helpers.py`
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/

---

**Ready to use!** The integrated system is production-ready and extends your existing chatbot with full message history tracking and session management. 🚀
