#!/usr/bin/env python3
"""
Test script for the production server

This script tests all endpoints of the production server.
Run this AFTER starting the server with deploy_local.py

Usage:
    python langchain1/test_server.py
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8002"

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_test(test_name):
    print(f"\n🧪 Testing: {test_name}")
    print("-" * 80)

def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_send_message(session_id="test-session-1"):
    """Test sending a message"""
    print_test("Send Message")
    
    try:
        payload = {
            "message": "Hello! What can you help me with?",
            "session_id": session_id
        }
        
        print(f"Sending: {payload['message']}")
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully")
            return True, session_id
        else:
            print("❌ Message send failed")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_memory(session_id):
    """Test memory with follow-up question"""
    print_test("Memory Test (Follow-up Question)")
    
    try:
        # First message
        payload1 = {
            "message": "My name is Alice and I love Python programming",
            "session_id": session_id
        }
        print(f"First message: {payload1['message']}")
        response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
        print(f"Response: {response1.json().get('response', 'N/A')[:100]}...")
        
        time.sleep(1)
        
        # Follow-up message to test memory
        payload2 = {
            "message": "What's my name and what do I love?",
            "session_id": session_id
        }
        print(f"\nFollow-up: {payload2['message']}")
        response2 = requests.post(f"{BASE_URL}/chat", json=payload2)
        result = response2.json()
        print(f"Response: {result.get('response', 'N/A')}")
        
        # Check if it remembers
        response_text = result.get('response', '').lower()
        if 'alice' in response_text and 'python' in response_text:
            print("✅ Memory working! Bot remembered the context")
            return True
        else:
            print("⚠️  Memory may not be working properly")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_query(session_id):
    """Test RAG integration"""
    print_test("RAG Integration Test")
    
    try:
        payload = {
            "message": "What is RAG? Search the documents.",
            "session_id": session_id
        }
        
        print(f"Sending: {payload['message']}")
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        result = response.json()
        
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ RAG query successful")
            return True
        else:
            print("❌ RAG query failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_history(session_id):
    """Test getting conversation history"""
    print_test("Get Conversation History")
    
    try:
        response = requests.get(f"{BASE_URL}/chat/{session_id}/history")
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"History: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print(f"✅ Retrieved {len(result.get('messages', []))} messages")
            return True
        else:
            print("❌ Failed to get history")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_sessions():
    """Test getting all sessions"""
    print_test("Get All Sessions")
    
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"Sessions: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print(f"✅ Found {len(result.get('sessions', []))} sessions")
            return True
        else:
            print("❌ Failed to get sessions")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    print_test("Metrics Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Metrics (first 500 chars):\n{response.text[:500]}...")
            print("✅ Metrics endpoint working")
            return True
        else:
            print("❌ Metrics endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_clear_session(session_id):
    """Test clearing a session"""
    print_test("Clear Session")
    
    try:
        response = requests.delete(f"{BASE_URL}/chat/{session_id}")
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Session cleared successfully")
            return True
        else:
            print("❌ Failed to clear session")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("🧪 LangChain1 Production Server - Test Suite")
    
    print(f"Testing server at: {BASE_URL}")
    print("Make sure the server is running with: python langchain1/deploy_local.py\n")
    
    # Check if server is up
    print("Checking if server is running...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ Server is running!\n")
    except:
        print("❌ Server is not running!")
        print("\nStart the server first with:")
        print("  python langchain1/deploy_local.py")
        print("\nOr manually:")
        print("  uvicorn langchain1.production_server:app --reload --port 8002")
        return 1
    
    # Run tests
    session_id = f"test-session-{int(time.time())}"
    results = {}
    
    results['Health Check'] = test_health_check()
    results['Send Message'], session_id = test_send_message(session_id)
    results['Memory Test'] = test_memory(session_id)
    results['RAG Query'] = test_rag_query(session_id)
    results['Get History'] = test_get_history(session_id)
    results['Get Sessions'] = test_get_sessions()
    results['Metrics'] = test_metrics()
    results['Clear Session'] = test_clear_session(session_id)
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test:30} {status}")
    
    print(f"\n{'='*80}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 All tests passed! Server is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
