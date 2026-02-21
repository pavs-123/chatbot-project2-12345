"""
Comprehensive test script for Memory and ReAct agents
Run this to see everything in action!
"""
import sys
from pathlib import Path

# Ensure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_memory():
    """Test all memory strategies"""
    print("=" * 80)
    print("🧠 TESTING MEMORY CHATBOT")
    print("=" * 80)
    
    try:
        from langchain1.memory_chatbot import (
            run_buffer_memory_example,
            run_summary_memory_example,
            run_entity_memory_example,
            run_window_memory_example
        )
        
        print("\n1️⃣ Buffer Memory (stores all messages)")
        print("-" * 80)
        run_buffer_memory_example()
        
        print("\n\n2️⃣ Summary Memory (summarizes old messages)")
        print("-" * 80)
        run_summary_memory_example()
        
        print("\n\n3️⃣ Entity Memory (tracks entities)")
        print("-" * 80)
        run_entity_memory_example()
        
        print("\n\n4️⃣ Window Memory (keeps last N messages)")
        print("-" * 80)
        run_window_memory_example()
        
        print("\n✅ All memory tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_react():
    """Test ReAct agent"""
    print("\n\n" + "=" * 80)
    print("🤖 TESTING REACT AGENT")
    print("=" * 80)
    
    try:
        from langchain1.react_agent import run_react_examples
        
        run_react_examples()
        
        print("\n✅ ReAct agent test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ReAct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_agent():
    """Test advanced agent (Memory + ReAct combined)"""
    print("\n\n" + "=" * 80)
    print("⭐ TESTING ADVANCED AGENT (Memory + ReAct + RAG + Weather)")
    print("=" * 80)
    
    try:
        from langchain1.advanced_agent import run_advanced_examples
        
        run_advanced_examples()
        
        print("\n✅ Advanced agent test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Advanced agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive LangGraph test suite...")
    print("This will test Memory, ReAct, and Advanced agents\n")
    
    results = {
        "Memory": test_memory(),
        "ReAct": test_react(),
        "Advanced": test_advanced_agent()
    }
    
    print("\n\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Your LangGraph system is working perfectly!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    print("=" * 80)
