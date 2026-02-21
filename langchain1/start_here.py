#!/usr/bin/env python3
"""
🚀 LangChain1 - Getting Started Script

This interactive script helps you get started with Memory and ReAct agents.
Run this first to understand what's available and how to use it!
"""
import os
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_section(number, title):
    """Print a section header"""
    print(f"\n{number}️⃣  {title}")
    print("-" * 80)

def main():
    print_header("🎉 Welcome to LangChain1 - Memory + ReAct Agent System!")
    
    print("""
This system provides:
  🧠 Memory Management - 4 different strategies
  🤖 ReAct Agent - Reasoning + Acting with tools
  📚 RAG Integration - Document search and retrieval
  🌤️  Weather API - Real-time weather data
  ⭐ Advanced Agent - Everything combined!
""")
    
    print_section("1", "What You Have")
    
    files = {
        "📓 Notebooks": [
            "langgraph_messages.ipynb - Basic LangGraph tutorial",
            "memory_notebook.ipynb - Memory strategies",
            "react_notebook.ipynb - ReAct agent with tools",
            "integrated_notebook.ipynb - Full integration demo"
        ],
        "🐍 Python Scripts": [
            "memory_chatbot.py - 4 memory strategies",
            "react_agent.py - ReAct reasoning agent",
            "advanced_agent.py - Combined system",
            "integrated_chatbot.py - Full integration",
            "custom_tools.py - Example custom tools"
        ],
        "🚀 Production": [
            "production_server.py - Production-ready FastAPI server",
            "integrated_api.py - API with sessions",
            "docker-compose.yml - Docker deployment",
            "Dockerfile - Container configuration"
        ],
        "📚 Documentation": [
            "QUICK_START.md - 5-minute guide",
            "MEMORY_REACT_GUIDE.md - Memory & ReAct patterns",
            "CUSTOM_TOOLS_GUIDE.md - Creating custom tools",
            "DEPLOYMENT_GUIDE.md - Production deployment",
            "JUPYTER_GUIDE.md - Jupyter notebook guide"
        ]
    }
    
    for category, items in files.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✓ {item}")
    
    print_section("2", "Quick Test - Run Examples")
    
    print("""
To test the system, run:

  python langchain1/test_all.py

This will test:
  - Buffer Memory (stores all messages)
  - Summary Memory (summarizes old messages)
  - Entity Memory (tracks people, places, things)
  - Window Memory (keeps last N messages)
  - ReAct Agent (reasoning with tools)
  - Advanced Agent (everything combined)
""")
    
    print_section("3", "Open Jupyter Notebooks")
    
    print("""
For interactive learning:

  jupyter notebook

Then open:
  1. memory_notebook.ipynb - Learn memory strategies
  2. react_notebook.ipynb - Learn ReAct patterns
  3. integrated_notebook.ipynb - See full integration

Or use VS Code with Jupyter extension!
""")
    
    print_section("4", "Customize with Your Own Tools")
    
    print("""
Check out custom_tools.py for examples:

  - Email tool (send emails)
  - Database tool (query databases)
  - File tool (read/write files)
  - API tool (call external APIs)
  - Scraper tool (scrape websites)

Read CUSTOM_TOOLS_GUIDE.md for details on creating your own!
""")
    
    print_section("5", "Deploy to Production")
    
    print("""
Three deployment options:

A. Local Development:
   uvicorn langchain1.production_server:app --reload --port 8002

B. Docker:
   docker-compose up -d

C. Cloud (AWS, GCP, Azure):
   See DEPLOYMENT_GUIDE.md for detailed instructions

The server includes:
  ✓ REST API endpoints
  ✓ WebSocket for streaming
  ✓ Session management
  ✓ Rate limiting
  ✓ Metrics & monitoring
  ✓ Health checks
""")
    
    print_section("6", "Environment Setup")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        print(f"⚠️  No .env file found!")
        print(f"\nTo set up your environment:")
        print(f"  1. Copy .env.example to .env")
        print(f"  2. Add your API keys (OpenAI, Anthropic, Groq, etc.)")
        print(f"  3. Configure your settings\n")
        
        if env_example.exists():
            print(f"Quick start:")
            print(f"  cp {env_example} {env_file}")
    else:
        print(f"✅ Found .env file at {env_file}")
    
    print_section("7", "Next Steps")
    
    print("""
Choose your path:

  🎓 Learning Path:
     1. Read QUICK_START.md (5 minutes)
     2. Run test_all.py
     3. Open memory_notebook.ipynb
     4. Open react_notebook.ipynb

  🔧 Developer Path:
     1. Read CUSTOM_TOOLS_GUIDE.md
     2. Study custom_tools.py
     3. Create your own tools
     4. Test with advanced_agent.py

  🚀 Production Path:
     1. Read DEPLOYMENT_GUIDE.md
     2. Configure .env file
     3. Test with production_server.py
     4. Deploy with Docker

  📚 Deep Dive Path:
     1. Read MEMORY_REACT_GUIDE.md
     2. Study the source code
     3. Read INTEGRATION_GUIDE.md
     4. Build your own agent
""")
    
    print_header("✨ Ready to Start!")
    
    print("""
Recommended first steps:

  1. Run the tests:
     python langchain1/test_all.py

  2. Open a notebook:
     jupyter notebook langchain1/memory_notebook.ipynb

  3. Read the quick start:
     cat langchain1/QUICK_START.md

Happy coding! 🎉
""")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
