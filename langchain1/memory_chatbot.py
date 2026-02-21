"""
LangGraph Chatbot with Memory Features

This module demonstrates different memory strategies:
1. ConversationBufferMemory - Store full conversation history
2. ConversationSummaryMemory - Summarize old messages
3. ConversationEntityMemory - Track entities (people, places, things)
4. ConversationWindowMemory - Keep only last N messages

Usage:
    python langchain1/memory_chatbot.py --query "My name is Alice" --memory-type buffer
    python langchain1/memory_chatbot.py --query "What's my name?" --session-id <id>
"""
from __future__ import annotations
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
import operator
import json
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chatbot.llm_provider import get_llm


# Memory storage (use Redis/DB in production)
MEMORY_DIR = Path(__file__).parent / ".memory"
MEMORY_DIR.mkdir(exist_ok=True)


class MemoryState(TypedDict):
    """Enhanced state with memory features."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    answer: str
    session_id: str
    
    # Memory fields
    conversation_summary: str
    entities: Dict[str, str]  # entity_name -> description
    message_count: int
    memory_type: str  # "buffer" | "summary" | "entity" | "window"
    window_size: int  # for window memory


def load_session_memory(session_id: str) -> Dict[str, Any]:
    """Load memory from disk."""
    memory_file = MEMORY_DIR / f"{session_id}.json"
    if memory_file.exists():
        with open(memory_file, 'r') as f:
            return json.load(f)
    return {
        "summary": "",
        "entities": {},
        "message_count": 0,
        "created_at": datetime.now().isoformat(),
    }


def save_session_memory(session_id: str, data: Dict[str, Any]):
    """Save memory to disk."""
    memory_file = MEMORY_DIR / f"{session_id}.json"
    data["updated_at"] = datetime.now().isoformat()
    with open(memory_file, 'w') as f:
        json.dump(data, f, indent=2)


def initialize_memory_node(state: MemoryState) -> MemoryState:
    """Initialize memory by loading previous conversation data."""
    session_id = state.get("session_id", "default")
    memory_data = load_session_memory(session_id)
    
    memory_type = state.get("memory_type", "buffer")
    
    # Create system message based on memory type
    if memory_type == "summary" and memory_data.get("summary"):
        sys_msg = SystemMessage(
            content=f"Conversation summary so far: {memory_data['summary']}\n\n"
                   f"Continue the conversation with this context in mind."
        )
    elif memory_type == "entity" and memory_data.get("entities"):
        entities_str = "\n".join([f"- {k}: {v}" for k, v in memory_data["entities"].items()])
        sys_msg = SystemMessage(
            content=f"Known entities from conversation:\n{entities_str}\n\n"
                   f"Use this information to provide personalized responses."
        )
    else:
        sys_msg = SystemMessage(
            content="Starting conversation with memory enabled. I will remember our discussion."
        )
    
    return {
        "messages": [sys_msg],
        "user_query": state.get("user_query", ""),
        "answer": "",
        "session_id": session_id,
        "conversation_summary": memory_data.get("summary", ""),
        "entities": memory_data.get("entities", {}),
        "message_count": memory_data.get("message_count", 0),
        "memory_type": memory_type,
        "window_size": state.get("window_size", 10),
    }


def extract_entities_node(state: MemoryState) -> MemoryState:
    """Extract entities (names, places, facts) from the conversation."""
    if state.get("memory_type") != "entity":
        return state  # Skip if not using entity memory
    
    query = state.get("user_query", "")
    llm = get_llm()
    
    # Prompt to extract entities
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract named entities (people, places, organizations, facts) from the user message. "
                  "Return as JSON: {\"entity_name\": \"description\"}. If no entities, return empty dict."),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    try:
        result = chain.invoke({"query": query})
        content = result.content if hasattr(result, 'content') else str(result)
        
        # Try to parse JSON
        if "{" in content and "}" in content:
            start = content.index("{")
            end = content.rindex("}") + 1
            entities_json = content[start:end]
            new_entities = json.loads(entities_json)
        else:
            new_entities = {}
        
        # Merge with existing entities
        entities = state.get("entities", {})
        entities.update(new_entities)
        
        if new_entities:
            sys_msg = SystemMessage(
                content=f"Extracted entities: {', '.join(new_entities.keys())}"
            )
            return {
                "messages": [sys_msg],
                "entities": entities,
            }
    except Exception as e:
        print(f"Entity extraction error: {e}")
    
    return state


def process_with_memory_node(state: MemoryState) -> MemoryState:
    """Process query with appropriate memory context."""
    query = state.get("user_query", "")
    memory_type = state.get("memory_type", "buffer")
    llm = get_llm()
    
    # Get relevant message history based on memory type
    all_messages = state.get("messages", [])
    
    if memory_type == "window":
        # Keep only last N messages
        window_size = state.get("window_size", 10)
        recent_messages = all_messages[-window_size:]
    elif memory_type == "summary":
        # Use summary + recent messages
        summary = state.get("conversation_summary", "")
        recent_messages = all_messages[-3:]  # Last 3 messages
        if summary:
            recent_messages = [SystemMessage(content=f"Previous context: {summary}")] + recent_messages
    else:
        # Buffer or entity - use all messages
        recent_messages = all_messages
    
    # Create prompt with memory
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with memory. Use the conversation history to provide contextual answers."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "query": query,
            "history": recent_messages
        })
        answer = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        answer = f"Error processing with memory: {e}"
    
    ai_msg = AIMessage(content=answer)
    
    return {
        "messages": [ai_msg],
        "answer": answer,
        "message_count": state.get("message_count", 0) + 1,
    }


def update_summary_node(state: MemoryState) -> MemoryState:
    """Update conversation summary (for summary memory type)."""
    if state.get("memory_type") != "summary":
        return state  # Skip if not using summary memory
    
    # Only update summary every N messages
    message_count = state.get("message_count", 0)
    if message_count % 5 != 0:  # Update every 5 messages
        return state
    
    llm = get_llm()
    messages = state.get("messages", [])
    
    # Get last few messages to summarize
    recent = messages[-10:]
    messages_text = "\n".join([
        f"{type(msg).__name__}: {msg.content}"
        for msg in recent
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following conversation concisely, focusing on key information and context."),
        ("human", "{messages}")
    ])
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({"messages": messages_text})
        new_summary = result.content if hasattr(result, 'content') else str(result)
        
        sys_msg = SystemMessage(content=f"Conversation summarized: {new_summary[:100]}...")
        
        return {
            "messages": [sys_msg],
            "conversation_summary": new_summary,
        }
    except Exception as e:
        print(f"Summary update error: {e}")
    
    return state


def save_memory_node(state: MemoryState) -> MemoryState:
    """Save memory to persistent storage."""
    session_id = state.get("session_id", "default")
    
    memory_data = {
        "summary": state.get("conversation_summary", ""),
        "entities": state.get("entities", {}),
        "message_count": state.get("message_count", 0),
        "memory_type": state.get("memory_type", "buffer"),
    }
    
    save_session_memory(session_id, memory_data)
    
    sys_msg = SystemMessage(content="Memory saved successfully.")
    
    return {
        "messages": [sys_msg],
    }


def build_memory_chatbot():
    """Build LangGraph with memory capabilities."""
    graph = StateGraph(MemoryState)
    
    # Add nodes
    graph.add_node("initialize_memory", initialize_memory_node)
    graph.add_node("extract_entities", extract_entities_node)
    graph.add_node("process_with_memory", process_with_memory_node)
    graph.add_node("update_summary", update_summary_node)
    graph.add_node("save_memory", save_memory_node)
    
    # Build flow
    graph.set_entry_point("initialize_memory")
    graph.add_edge("initialize_memory", "extract_entities")
    graph.add_edge("extract_entities", "process_with_memory")
    graph.add_edge("process_with_memory", "update_summary")
    graph.add_edge("update_summary", "save_memory")
    graph.add_edge("save_memory", END)
    
    return graph.compile()


def print_memory_state(state: MemoryState):
    """Pretty print memory state."""
    print("\n" + "="*70)
    print("MEMORY STATE")
    print("="*70)
    print(f"Session ID: {state.get('session_id', 'N/A')}")
    print(f"Memory Type: {state.get('memory_type', 'N/A')}")
    print(f"Message Count: {state.get('message_count', 0)}")
    
    if state.get("conversation_summary"):
        print(f"\nSummary: {state['conversation_summary'][:200]}...")
    
    if state.get("entities"):
        print("\nEntities:")
        for name, desc in state["entities"].items():
            print(f"  - {name}: {desc}")
    
    print("\n" + "-"*70)
    print(f"Query: {state.get('user_query', 'N/A')}")
    print(f"Answer: {state.get('answer', 'N/A')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    import uuid
    
    parser = argparse.ArgumentParser(description="Memory-enabled Chatbot")
    parser.add_argument("--query", "-q", required=True, help="Your question")
    parser.add_argument("--session-id", default=str(uuid.uuid4()), help="Session ID (creates new if not provided)")
    parser.add_argument("--memory-type", choices=["buffer", "summary", "entity", "window"], 
                       default="buffer", help="Memory type")
    parser.add_argument("--window-size", type=int, default=10, help="Window size for window memory")
    parser.add_argument("--visualize", action="store_true", help="Show graph")
    args = parser.parse_args()
    
    # Build chatbot
    chatbot = build_memory_chatbot()
    
    # Visualize
    if args.visualize:
        try:
            print("\n📊 Memory Chatbot Graph:\n")
            print(chatbot.get_graph().draw_ascii())
        except Exception as e:
            print(f"Could not visualize: {e}")
    
    # Create initial state
    initial_state = MemoryState(
        messages=[HumanMessage(content=args.query)],
        user_query=args.query,
        answer="",
        session_id=args.session_id,
        conversation_summary="",
        entities={},
        message_count=0,
        memory_type=args.memory_type,
        window_size=args.window_size,
    )
    
    # Run
    print(f"\n🤖 Processing with {args.memory_type} memory...")
    print(f"Session ID: {args.session_id}")
    result = chatbot.invoke(initial_state)
    
    # Print result
    print_memory_state(result)
    
    print(f"\n💡 To continue this conversation, use: --session-id {args.session_id}")
