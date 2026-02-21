# 🎯 LangGraph Examples & Use Cases

This document provides practical examples for all the LangGraph features.

## 📚 Table of Contents

1. [Basic Examples](#basic-examples)
2. [Memory Examples](#memory-examples)
3. [ReAct Agent Examples](#react-agent-examples)
4. [Advanced Agent Examples](#advanced-agent-examples)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Basic Examples

### Example 1: Simple Message Flow
```bash
python langchain1/run_example.py
```

**Output:**
```
[HumanMessage] What is AI?
[SystemMessage] Initializing context...
[AIMessage] AI stands for Artificial Intelligence...
```

### Example 2: Integrated Chatbot (RAG)
```bash
python langchain1/integrated_chatbot.py --query "What is RAG?"
```

**How it works:**
1. Detects intent → RAG
2. Searches knowledge base
3. Generates answer with sources

### Example 3: Weather Query
```bash
python langchain1/integrated_chatbot.py --query "Weather in Tokyo?"
```

**How it works:**
1. Detects intent → Weather
2. Geocodes "Tokyo"
3. Fetches weather data
4. Formats response

---

## Memory Examples

### Example 1: Buffer Memory (Full History)
```bash
# First message
python langchain1/memory_chatbot.py \
  --query "My name is Alice" \
  --memory-type buffer

# Second message (remembers everything)
python langchain1/memory_chatbot.py \
  --query "What's my name?" \
  --session-id <session-id> \
  --memory-type buffer
```

**Use Case:** Short conversations where you need full context.

### Example 2: Entity Memory (Track Facts)
```bash
# Introduce yourself
python langchain1/memory_chatbot.py \
  --query "I'm Bob, I live in Paris, and I love Python" \
  --memory-type entity

# Ask about yourself
python langchain1/memory_chatbot.py \
  --query "Where do I live?" \
  --session-id <id> \
  --memory-type entity
```

**Entities Tracked:**
- Name: Bob
- Location: Paris
- Interest: Python

**Use Case:** Long conversations where you need to remember specific facts.

### Example 3: Summary Memory (Long Conversations)
```bash
# Have a long conversation (10+ messages)
python langchain1/memory_chatbot.py \
  --query "Tell me about AI" \
  --memory-type summary

# Continue - old messages are summarized
python langchain1/memory_chatbot.py \
  --query "What did we discuss?" \
  --session-id <id> \
  --memory-type summary
```

**Use Case:** Very long conversations where full history is too large.

### Example 4: Window Memory (Recent Only)
```bash
python langchain1/memory_chatbot.py \
  --query "Message 1" \
  --memory-type window \
  --window-size 5

# Only remembers last 5 messages
```

**Use Case:** When you only need recent context.

---

## ReAct Agent Examples

### Example 1: Math Calculation
```bash
python langchain1/react_agent.py --query "What is 25 * 47?"
```

**Trace:**
```
💭 [Step 1] Thought: I need to calculate 25 * 47
🔧 Action: calculator
🔧 Action Input: 25 * 47
🔧 Result: 1175
💭 [Step 2] Thought: I have the answer
✅ FINAL: The result is 1175
```

### Example 2: Weather + Math
```bash
python langchain1/react_agent.py \
  --query "Get Paris weather and multiply temperature by 2"
```

**Trace:**
```
💭 [Step 1] Thought: First get weather for Paris
🔧 Action: get_weather
🔧 Action Input: Paris
🔧 Result: Weather in Paris: 15°C, wind 10 km/h
💭 [Step 2] Thought: Now multiply 15 by 2
🔧 Action: calculator
🔧 Action Input: 15 * 2
🔧 Result: 30
💭 [Step 3] Thought: I can answer now
✅ FINAL: The temperature in Paris is 15°C. Multiplied by 2 is 30°C.
```

### Example 3: Knowledge Base Search
```bash
python langchain1/react_agent.py \
  --query "Search for information about RAG in the knowledge base"
```

**Trace:**
```
💭 [Step 1] Thought: I should search the knowledge base
🔧 Action: search_knowledge_base
🔧 Action Input: RAG
🔧 Result: RAG stands for Retrieval-Augmented Generation...
💭 [Step 2] Thought: I have the information
✅ FINAL: According to the knowledge base, RAG stands for...
```

### Example 4: Python Execution
```bash
python langchain1/react_agent.py \
  --query "Calculate the sum of numbers from 1 to 10 using Python"
```

**Trace:**
```
💭 [Step 1] Thought: I'll use Python to calculate this
🔧 Action: python_repl
🔧 Action Input: print(sum(range(1, 11)))
🔧 Result: 55
💭 [Step 2] Thought: I have the result
✅ FINAL: The sum of numbers from 1 to 10 is 55
```

---

## Advanced Agent Examples

### Example 1: Memory + Reasoning
```bash
# Tell it your name and location
python langchain1/advanced_agent.py \
  --query "My name is Carol and I live in Berlin"

# Ask about weather where you live (it remembers!)
python langchain1/advanced_agent.py \
  --query "What's the weather where I live?" \
  --session-id <id>
```

**How it works:**
1. **First query:** Extracts entities (name: Carol, location: Berlin)
2. **Second query:** 
   - Loads memory: "user_location: Berlin"
   - Auto-detects "weather" keyword → ReAct mode
   - Uses entity to get weather for Berlin
   - Returns personalized answer

### Example 2: Auto Mode Detection
```bash
# Simple question → Simple mode
python langchain1/advanced_agent.py \
  --query "Hello, how are you?"

# Complex task → ReAct mode (auto-detected)
python langchain1/advanced_agent.py \
  --query "Calculate 100 * 50 and tell me if it's more than 4000"
```

**Mode Detection:**
- Simple: Greetings, questions without calculations
- ReAct: Math, weather, "calculate", "search", tools

### Example 3: Multi-Turn Conversation
```bash
# Turn 1: Introduce yourself
python langchain1/advanced_agent.py \
  --query "I'm David, I live in London, I'm learning Python"

# Turn 2: Simple question (uses memory)
python langchain1/advanced_agent.py \
  --query "What am I learning?" \
  --session-id <id>

# Turn 3: Complex task (uses memory + tools)
python langchain1/advanced_agent.py \
  --query "Get the weather where I live and multiply the temperature by 2" \
  --session-id <id>
```

**Memory Used:**
- Name: David
- Location: London
- Interest: Python

---

## Real-World Use Cases

### Use Case 1: Personal Assistant
```bash
# Setup
python langchain1/advanced_agent.py \
  --query "I'm Alice, I live in NYC, I work at TechCorp"

# Daily queries
python langchain1/advanced_agent.py \
  --query "What's the weather where I live?" \
  --session-id <id>

python langchain1/advanced_agent.py \
  --query "Calculate my work hours: 9am to 5:30pm with 30min lunch" \
  --session-id <id>
```

### Use Case 2: Research Assistant
```bash
# Search knowledge base
python langchain1/react_agent.py \
  --query "Search for RAG and explain how it works"

# Follow-up with calculation
python langchain1/react_agent.py \
  --query "If RAG improves accuracy by 25%, what's the new accuracy from 80%?"
```

### Use Case 3: Travel Planning
```bash
python langchain1/advanced_agent.py \
  --query "I'm planning to visit Paris and Tokyo"

python langchain1/advanced_agent.py \
  --query "What's the weather in the cities I'm visiting?" \
  --session-id <id>

python langchain1/advanced_agent.py \
  --query "Calculate the time difference between these cities" \
  --session-id <id>
```

### Use Case 4: Customer Support Bot
```bash
# Customer identifies
python langchain1/advanced_agent.py \
  --query "I'm customer John, my account ID is 12345"

# Query knowledge base
python langchain1/advanced_agent.py \
  --query "Search for information about refund policy" \
  --session-id <id>

# Calculate refund
python langchain1/advanced_agent.py \
  --query "Calculate 80% refund on $150" \
  --session-id <id>
```

---

## 🎓 Learning Path

### Beginner
1. Start with `run_example.py`
2. Try `integrated_chatbot.py` with simple queries
3. Experiment with `memory_chatbot.py` (buffer mode)

### Intermediate
1. Try `react_agent.py` with math queries
2. Use `memory_chatbot.py` with entity mode
3. Combine tools in `react_agent.py`

### Advanced
1. Use `advanced_agent.py` for multi-turn conversations
2. Build custom tools
3. Integrate with your own systems

---

## 💡 Tips & Tricks

### Memory Tips
- **Buffer**: Best for < 20 messages
- **Entity**: Best when you need to track facts
- **Summary**: Best for 50+ messages
- **Window**: Best when only recent context matters

### ReAct Tips
- Be specific with queries: "Calculate X" not "What is X"
- Chain tools: "Get weather AND calculate"
- Check tool descriptions to know what's available

### Advanced Agent Tips
- Use `--mode auto` for best results
- Save session IDs for multi-turn conversations
- Entity extraction works best with clear statements: "My name is X"

---

## 🐛 Troubleshooting

### Memory not persisting?
Check: `langchain1/.memory/` folder for session files

### ReAct not using tools?
Make query more explicit: "Use calculator to compute X"

### Entity not extracted?
Use clear patterns: "My name is...", "I live in..."

---

## 🚀 Next Steps

- Read `MEMORY_REACT_GUIDE.md` for technical details
- Read `INTEGRATION_GUIDE.md` for integration patterns
- Build your own custom tools
- Extend the agents with new capabilities

Happy building! 🎉
