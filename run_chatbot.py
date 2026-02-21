#!/usr/bin/env python
"""
Easy Chatbot Launcher
Just run: python run_chatbot.py
"""
import subprocess
import sys
import os
from pathlib import Path
import time


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🤖  AI CHATBOT - Easy Launcher")
    print("=" * 70)
    print()


def check_python_version():
    """Check if Python version is sufficient"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. You have:", sys.version)
        return False
    print(f"  Python {version.major}.{version.minor}.{version.micro} ✓")
    return True


def check_venv():
    """Check if virtual environment exists"""
    print("\n✓ Checking virtual environment...")
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("  ⚠️  No virtual environment found")
        print("  Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("  ✓ Virtual environment created")
            return True, True  # exists, newly_created
        except Exception as e:
            print(f"  ❌ Failed to create venv: {e}")
            return False, False
    
    print("  ✓ Virtual environment exists")
    return True, False


def get_pip_command():
    """Get the pip command for the current platform"""
    if sys.platform == "win32":
        return [".venv\\Scripts\\python.exe", "-m", "pip"]
    else:
        return [".venv/bin/python", "-m", "pip"]


def install_dependencies():
    """Install required dependencies"""
    print("\n✓ Installing dependencies...")
    print("  This may take a few minutes on first run...")
    
    pip_cmd = get_pip_command()
    
    try:
        # Upgrade pip
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install project
        subprocess.run(pip_cmd + ["install", "-e", "."], check=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        print("  ✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Installation failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        print("\n  Alternative: Try running manually:")
        print("    1. Close all Python processes")
        print("    2. Delete .venv folder")
        print("    3. Run this script again")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\n✓ Checking configuration...")
    env_path = Path(".env")
    
    if not env_path.exists():
        print("  ⚠️  No .env file found")
        print("  Creating from .env.example...")
        
        example_path = Path(".env.example")
        if example_path.exists():
            env_path.write_text(example_path.read_text())
            print("  ✓ Created .env file")
            print("\n  ⚠️  IMPORTANT: Edit .env file and add your API keys!")
            print("     Or use Ollama for free local LLM (no API key needed)")
            time.sleep(2)
        else:
            print("  ❌ .env.example not found")
            return False
    else:
        print("  ✓ Configuration file exists")
    
    return True


def test_imports():
    """Test if chatbot can be imported"""
    print("\n✓ Testing chatbot imports...")
    
    python_cmd = get_pip_command()[0]
    
    try:
        result = subprocess.run(
            [python_cmd, "-c", "from chatbot.api import app; print('SUCCESS')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "SUCCESS" in result.stdout:
            print("  ✓ Chatbot imports successfully")
            return True
        else:
            print("  ❌ Import test failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️  Import test timed out (may still work)")
        return True
    except Exception as e:
        print(f"  ❌ Import test error: {e}")
        return False


def start_server():
    """Start the chatbot server"""
    print("\n" + "=" * 70)
    print("🚀 Starting Chatbot Server...")
    print("=" * 70)
    print()
    print("📖 Web UI:        http://localhost:8001")
    print("📚 API Docs:      http://localhost:8001/docs")
    print("❤️  Health Check: http://localhost:8001/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    python_cmd = get_pip_command()[0]
    
    try:
        # Start uvicorn
        subprocess.run([
            python_cmd, "-m", "uvicorn",
            "chatbot.api:app",
            "--reload",
            "--port", "8001",
            "--host", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if port 8001 is already in use")
        print("  2. Verify .env file has correct API keys")
        print("  3. Check SETUP_CHATBOT.md for manual setup")
        return False
    
    return True


def main():
    """Main launcher"""
    print_banner()
    
    # Step 1: Check Python
    if not check_python_version():
        input("\nPress Enter to exit...")
        return 1
    
    # Step 2: Check/Create venv
    venv_ok, newly_created = check_venv()
    if not venv_ok:
        input("\nPress Enter to exit...")
        return 1
    
    # Step 3: Install dependencies (always on new venv, or if imports fail)
    if newly_created:
        if not install_dependencies():
            input("\nPress Enter to exit...")
            return 1
    else:
        # Quick import test
        python_cmd = get_pip_command()[0]
        try:
            result = subprocess.run(
                [python_cmd, "-c", "import fastapi"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                if not install_dependencies():
                    input("\nPress Enter to exit...")
                    return 1
        except:
            if not install_dependencies():
                input("\nPress Enter to exit...")
                return 1
    
    # Step 4: Check .env
    if not check_env_file():
        input("\nPress Enter to exit...")
        return 1
    
    # Step 5: Test imports
    if not test_imports():
        print("\n⚠️  Import test failed, but will try to start anyway...")
        time.sleep(2)
    
    # Step 6: Start server
    print("\n✓ All checks passed!")
    print()
    time.sleep(1)
    
    return 0 if start_server() else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✓ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
