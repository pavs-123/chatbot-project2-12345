# ⚡ Quick Start Guide

Get up and running with LangGraph in 5 minutes!

## 🎯 Choose Your Path

### Path 1: "I want to learn the basics" 📚

**Start here:** Basic example
```bash
python langchain1/run_example.py
```

**Then:** Open a notebook
```bash
jupyter notebook langchain1/langgraph_messages.ipynb
```

**Time:** 5-10 minutes

---

### Path 2: "I want memory features" 🧠

**Try this:**
```bash
# First conversation
python langchain1/memory_chatbot.py --query "My name is Alice and I love Python" --memory-type entity

# Copy the session ID from output, then:
python langchain1/memory_chatbot.py --query "What do I love?" --session-id YOUR_SESSION_ID --memory-type entity
```

**It remembers!** ✨

**Time:** 2 minutes

---

### Path 3: "I want an AI that can use tools" 🤖

**Try this:**
```bash
# Math calculation with reasoning
python langchain1/react_agent.py --query "What is 25 * 47 + 100?"

# Weather + Math combined
python langchain1/react_agent.py --query "Get Paris weather and multiply temperature by 2"
```

**Watch it reason through the steps!** 💭→🔧→✅

**Time:** 2 minutes

---

### Path 4: "I want the best of everything" 🚀

**Try this:**
```bash
# Tell it about yourself
python langchain1/advanced_agent.py --query "I'm Bob and I live in Tokyo"

# Copy the session ID, then ask:
python langchain1/advanced_agent.py --query "What's the weather where I live?" --session-id YOUR_SESSION_ID
```

**It remembers AND uses tools!** 🧠+🤖=🚀

**Time:** 3 minutes

---

### Path 5: "I want to integrate with my chatbot" 🔌

**Try this:**
```bash
# RAG query
python langchain1/integrated_chatbot.py --query "What is RAG?" --visualize

# Weather query
python langchain1/integrated_chatbot.py --query "Weather in London?"
```

**Time:** 2 minutes

---

### Path 6: "I want an API server" 🌐

**Start server:**
```bash
uvicorn langchain1.integrated_api:app --reload --port 8002
```

**Visit:** http://localhost:8002

**Test with curl:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?"}'
```

**Time:** 3 minutes

---

## 📊 Feature Comparison

| Feature | Basic | Integrated | Memory | ReAct | Advanced |
|---------|-------|------------|--------|-------|----------|
| Messages | ✅ | ✅ | ✅ | ✅ | ✅ |
| RAG | ❌ | ✅ | ❌ | ✅ | ✅ |
| Weather | ❌ | ✅ | ❌ | ✅ | ✅ |
| Memory | ❌ | ❌ | ✅ | ❌ | ✅ |
| Tools | ❌ | ❌ | ❌ | ✅ | ✅ |
| Reasoning | ❌ | ❌ | ❌ | ✅ | ✅ |
| Sessions | ❌ | ❌ | ✅ | ❌ | ✅ |

**Recommendation:** Start with Basic, then jump to Advanced! 🚀

---

## 🎓 Learning Order

### Beginner (30 minutes)
1. `run_example.py` - See basic LangGraph
2. `langgraph_messages.ipynb` - Interactive tutorial
3. `integrated_chatbot.py` - See RAG + Weather integration

### Intermediate (1 hour)
4. `memory_notebook.ipynb` - Learn memory strategies
5. `react_notebook.ipynb` - Learn ReAct pattern
6. `memory_chatbot.py` - Try entity memory
7. `react_agent.py` - Try different tools

### Advanced (2 hours)
8. `advanced_agent.py` - Use the ultimate agent
9. `integrated_api.py` - Run the API server
10. `INTEGRATION_GUIDE.md` - Deep dive into architecture
11. `EXAMPLES.md` - Real-world use cases

---

## 💡 Common Commands

### Memory Chatbot
```bash
# Buffer (full history)
python langchain1/memory_chatbot.py --query "Hello" --memory-type buffer

# Entity (track facts)
python langchain1/memory_chatbot.py --query "I'm Alice from Paris" --memory-type entity

# Summary (long conversations)
python langchain1/memory_chatbot.py --query "Tell me about AI" --memory-type summary

# Window (recent only)
python langchain1/memory_chatbot.py --query "Recent context" --memory-type window --window-size 5
```

### ReAct Agent
```bash
# Calculator
python langchain1/react_agent.py --query "Calculate 100 * 50"

# Weather
python langchain1/react_agent.py --query "Get weather for Tokyo"

# RAG search
python langchain1/react_agent.py --query "Search for RAG information"

# Python code
python langchain1/react_agent.py --query "Calculate sum of 1 to 10 using Python"

# Combined
python langchain1/react_agent.py --query "Get Paris weather and multiply temperature by 2"
```

### Advanced Agent
```bash
# Simple mode (auto-detected)
python langchain1/advanced_agent.py --query "Hello, how are you?"

# ReAct mode (auto-detected)
python langchain1/advanced_agent.py --query "Calculate 25 * 47"

# Force mode
python langchain1/advanced_agent.py --query "Your question" --mode react

# Visualize graph
python langchain1/advanced_agent.py --query "Test" --visualize
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'langgraph'"
**Solution:**
```bash
pip install langgraph langchain langchain-core
```

### Issue: "OPENAI_API_KEY not set"
**Solution:**
1. Create `.env` file in project root
2. Add: `OPENAI_API_KEY=your-key-here`

**OR** use Ollama (free, local):
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3.2

# Set environment variable
export CHATBOT_LLM_PROVIDER=ollama
```

### Issue: "Memory not persisting"
**Check:** Files are saved in `langchain1/.memory/`

**Solution:** Make sure you use the same `--session-id`

### Issue: "ReAct not using tools"
**Solution:** Be more explicit: "Use calculator to compute X"

---

## 🎯 Next Steps

After trying the examples:

1. **Read the guides:**
   - `README.md` - Full user guide
   - `MEMORY_REACT_GUIDE.md` - Advanced patterns
   - `INTEGRATION_GUIDE.md` - Technical details
   - `EXAMPLES.md` - Real-world use cases

2. **Experiment:**
   - Try different memory types
   - Combine multiple tools
   - Build multi-turn conversations

3. **Customize:**
   - Add your own tools
   - Modify the prompts
   - Integrate with your systems

4. **Deploy:**
   - Use the API server
   - Add authentication
   - Connect to database

---

## 🚀 Ready to Start?

Pick a path above and run the command! 

**Need help?** Check the documentation files or ask questions.

**Happy coding!** 🎉
