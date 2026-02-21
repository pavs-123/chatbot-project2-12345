#!/usr/bin/env python3
"""
Local Deployment Helper for LangChain1 Production Server

This script:
1. Checks dependencies
2. Validates configuration
3. Sets up environment
4. Starts the production server

Usage:
    python langchain1/deploy_local.py
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_step(step, text):
    """Print step"""
    print(f"\n{step}. {text}")
    print("-" * 80)

def check_dependencies():
    """Check if required packages are installed"""
    print_step("1", "Checking Dependencies")
    
    required = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'langchain': 'LangChain framework',
        'langgraph': 'LangGraph library',
        'pydantic': 'Data validation',
    }
    
    missing = []
    installed = []
    
    for package, description in required.items():
        try:
            __import__(package)
            installed.append(f"  ✅ {package:20} - {description}")
        except ImportError:
            missing.append(f"  ❌ {package:20} - {description}")
    
    if installed:
        print("Installed packages:")
        for item in installed:
            print(item)
    
    if missing:
        print("\nMissing packages:")
        for item in missing:
            print(item)
        print("\nInstall missing packages with:")
        print("  pip install -r langchain1/requirements.txt")
        return False
    
    print("\n✅ All required dependencies installed!")
    return True

def check_environment():
    """Check environment configuration"""
    print_step("2", "Checking Environment Configuration")
    
    env_file = Path("langchain1/.env")
    env_example = Path("langchain1/.env.example")
    
    if env_file.exists():
        print(f"✅ Found .env file at: {env_file}")
        
        # Load and check critical variables
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        critical_vars = {
            'OPENAI_API_KEY': 'OpenAI API (optional)',
            'SERVER_PORT': 'Server port (default: 8002)',
        }
        
        print("\nEnvironment variables:")
        for var, desc in critical_vars.items():
            value = os.getenv(var)
            if value:
                masked = value[:8] + "..." if len(value) > 8 else value
                print(f"  ✅ {var:20} = {masked} ({desc})")
            else:
                print(f"  ⚠️  {var:20} = Not set ({desc})")
        
        return True
    else:
        print(f"⚠️  No .env file found at: {env_file}")
        if env_example.exists():
            print(f"\n💡 Create one from the example:")
            print(f"   cp {env_example} {env_file}")
            print(f"   # Then edit {env_file} and add your API keys")
        print("\n⚠️  Server will start with default configuration")
        return True

def check_integrations():
    """Check if integrated systems are available"""
    print_step("3", "Checking Integrations")
    
    checks = {
        'RAG System': Path('rag/app.py'),
        'Weather API': Path('mcp_weather/api.py'),
        'Chatbot': Path('chatbot/graph.py'),
    }
    
    for name, path in checks.items():
        if path.exists():
            print(f"  ✅ {name:20} - {path}")
        else:
            print(f"  ⚠️  {name:20} - Not found at {path}")
    
    return True

def start_server(port=8002, reload=True):
    """Start the production server"""
    print_step("4", "Starting Production Server")
    
    print(f"""
Server Configuration:
  Host: 0.0.0.0 (accessible from network)
  Port: {port}
  Reload: {reload}
  
Endpoints:
  📖 API Docs:        http://localhost:{port}/docs
  🔄 Alternative:     http://localhost:{port}/redoc
  ❤️  Health Check:   http://localhost:{port}/health
  📊 Metrics:         http://localhost:{port}/metrics
  
WebSocket:
  🔌 Chat Stream:     ws://localhost:{port}/ws/chat/{{session_id}}
  
REST API:
  💬 Send Message:    POST http://localhost:{port}/chat
  📜 Get History:     GET  http://localhost:{port}/chat/{{session_id}}/history
  🗑️  Clear Session:  DELETE http://localhost:{port}/chat/{{session_id}}
  📊 Get Sessions:    GET  http://localhost:{port}/sessions
""")
    
    print("=" * 80)
    print("🚀 Starting server... (Press Ctrl+C to stop)")
    print("=" * 80 + "\n")
    
    # Start uvicorn
    cmd = [
        "uvicorn",
        "langchain1.production_server:app",
        "--host", "0.0.0.0",
        "--port", str(port),
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped gracefully")
    except FileNotFoundError:
        print("\n❌ uvicorn not found. Install it with:")
        print("   pip install uvicorn[standard]")
        return False
    
    return True

def main():
    """Main deployment function"""
    print_header("🚀 LangChain1 Production Server - Local Deployment")
    
    print("""
This script will:
  1. Check dependencies
  2. Validate configuration  
  3. Check integrations
  4. Start the production server
  
Press Ctrl+C at any time to stop.
""")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return 1
    
    # Step 2: Check environment
    check_environment()
    
    # Step 3: Check integrations
    check_integrations()
    
    # Step 4: Get port from environment or use default
    try:
        from dotenv import load_dotenv
        load_dotenv("langchain1/.env", override=False)
    except ImportError:
        pass
    
    port = int(os.getenv("SERVER_PORT", 8002))
    
    # Step 5: Start server
    print("\n" + "=" * 80)
    input("Press Enter to start the server...")
    
    start_server(port=port, reload=True)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
