"""
Advanced LangGraph Agent: Memory + ReAct + RAG + Weather

This combines:
1. Memory (conversation history, entities, summaries)
2. ReAct pattern (reasoning + acting)
3. Tools (Calculator, RAG, Weather, Python)
4. Session management

Usage:
    # Start a conversation with memory
    python langchain1/advanced_agent.py --query "My name is Alice and I live in Paris"
    
    # Continue with the same session (it remembers you!)
    python langchain1/advanced_agent.py --query "What's the weather where I live?" --session-id <id>
    
    # Complex reasoning task
    python langchain1/advanced_agent.py --query "Calculate 25*47 and tell me if it's more than 1000"
"""
from __future__ import annotations
from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Literal
import operator
import json
import uuid
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chatbot.llm_provider import get_llm, get_embeddings

# Import tools from react_agent
from langchain1.react_agent import TOOLS, calculator, search_knowledge_base, get_weather, python_repl

# Memory storage
MEMORY_DIR = Path(__file__).parent / ".memory"
MEMORY_DIR.mkdir(exist_ok=True)


class AdvancedAgentState(TypedDict):
    """Combined state with memory and ReAct capabilities."""
    # Messages
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    
    # Memory
    session_id: str
    conversation_summary: str
    entities: Dict[str, str]
    message_count: int
    
    # ReAct
    thought: str
    action: str
    action_input: str
    observation: str
    final_answer: str
    iteration: int
    max_iterations: int
    
    # Control
    mode: str  # "simple" | "react" | "auto"


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
        "messages_history": [],
        "created_at": datetime.now().isoformat(),
    }


def save_session_memory(session_id: str, data: Dict[str, Any]):
    """Save memory to disk."""
    memory_file = MEMORY_DIR / f"{session_id}.json"
    data["updated_at"] = datetime.now().isoformat()
    with open(memory_file, 'w') as f:
        json.dump(data, f, indent=2)


def initialize_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Initialize agent with memory and context."""
    session_id = state.get("session_id", str(uuid.uuid4()))
    memory_data = load_session_memory(session_id)
    
    # Build context from memory
    context_parts = ["You are an advanced AI assistant with memory and reasoning capabilities."]
    
    if memory_data.get("summary"):
        context_parts.append(f"\nConversation summary: {memory_data['summary']}")
    
    if memory_data.get("entities"):
        entities_str = ", ".join([f"{k} ({v})" for k, v in memory_data["entities"].items()])
        context_parts.append(f"\nKnown entities: {entities_str}")
    
    sys_msg = SystemMessage(content="\n".join(context_parts))
    
    return {
        "messages": [sys_msg],
        "user_query": state.get("user_query", ""),
        "session_id": session_id,
        "conversation_summary": memory_data.get("summary", ""),
        "entities": memory_data.get("entities", {}),
        "message_count": memory_data.get("message_count", 0),
        "thought": "",
        "action": "",
        "action_input": "",
        "observation": "",
        "final_answer": "",
        "iteration": 0,
        "max_iterations": state.get("max_iterations", 5),
        "mode": state.get("mode", "auto"),
    }


def route_decision_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Decide whether to use simple response or ReAct reasoning."""
    mode = state.get("mode", "auto")
    query = state.get("user_query", "").lower()
    
    # Auto-detect if ReAct is needed
    if mode == "auto":
        # Use ReAct for: calculations, multi-step tasks, tool usage keywords
        needs_react = any([
            "calculate" in query,
            "weather" in query,
            "multiply" in query,
            "divide" in query,
            "search" in query,
            "find" in query,
            "+" in query,
            "*" in query,
            "/" in query,
            "-" in query and query.count("-") == 1,  # subtraction, not hyphen
        ])
        
        mode = "react" if needs_react else "simple"
    
    sys_msg = SystemMessage(
        content=f"Mode selected: {mode.upper()} - "
                f"{'Using reasoning and tools' if mode == 'react' else 'Direct response'}"
    )
    
    return {
        "messages": [sys_msg],
        "mode": mode,
    }


def simple_response_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Simple conversational response with memory context."""
    query = state.get("user_query", "")
    messages = state.get("messages", [])
    
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use conversation history to provide contextual responses."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "query": query,
            "history": messages[-10:]  # Last 10 messages
        })
        answer = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        answer = f"Error: {e}"
    
    ai_msg = AIMessage(content=answer)
    
    return {
        "messages": [ai_msg],
        "final_answer": answer,
    }


def react_reasoning_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """ReAct reasoning with memory context."""
    query = state.get("user_query", "")
    messages = state.get("messages", [])
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 5)
    entities = state.get("entities", {})
    
    if iteration >= max_iterations:
        return {
            "final_answer": "Maximum iterations reached.",
            "iteration": iteration,
        }
    
    # Build context with entities
    entity_context = ""
    if entities:
        entity_context = "Known context: " + ", ".join([f"{k}: {v}" for k, v in entities.items()])
    
    tools_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in TOOLS.items()])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a ReAct agent with memory.\n"
         "{entity_context}\n\n"
         "Follow this pattern:\n"
         "Thought: Reason about what to do\n"
         "Action: Tool to use ({tools})\n"
         "Action Input: Tool input\n\n"
         "Or if ready:\n"
         "Thought: I can answer now\n"
         "Final Answer: Your answer"),
        ("human", "Task: {query}\n\nObservations so far:\n{history}\n\nNext step?")
    ])
    
    history = "\n".join([
        msg.content for msg in messages
        if isinstance(msg, (ToolMessage, SystemMessage))
    ][-5:])
    
    llm = get_llm()
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "query": query,
            "tools": ", ".join(TOOLS.keys()),
            "entity_context": entity_context,
            "history": history or "None"
        })
        response = result.content if hasattr(result, 'content') else str(result)
        
        # Parse
        thought = ""
        action = ""
        action_input = ""
        final_answer = ""
        
        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
            thought = response.split("Thought:")[-1].split("Final Answer:")[0].strip() if "Thought:" in response else ""
        else:
            if "Thought:" in response:
                thought = response.split("Thought:")[-1].split("Action:")[0].strip()
            if "Action:" in response:
                action = response.split("Action:")[-1].split("Action Input:")[0].strip()
            if "Action Input:" in response:
                action_input = response.split("Action Input:")[-1].strip()
        
        sys_msg = SystemMessage(content=f"[Step {iteration + 1}] Thought: {thought}")
        
        return {
            "messages": [sys_msg],
            "thought": thought,
            "action": action.strip(),
            "action_input": action_input.strip(),
            "final_answer": final_answer,
            "iteration": iteration + 1,
        }
    except Exception as e:
        return {
            "final_answer": f"Error: {e}",
            "iteration": iteration + 1,
        }


def react_action_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Execute tool action."""
    action = state.get("action", "").lower().replace(" ", "_")
    action_input = state.get("action_input", "")
    
    if not action or action not in TOOLS:
        observation = f"Invalid tool '{action}'. Available: {', '.join(TOOLS.keys())}"
    else:
        try:
            tool = TOOLS[action]
            observation = tool.invoke(action_input)
        except Exception as e:
            observation = f"Tool error: {e}"
    
    tool_msg = ToolMessage(content=f"Result: {observation}", tool_call_id=action)
    
    return {
        "messages": [tool_msg],
        "observation": observation,
    }


def extract_entities_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Extract entities from conversation for memory."""
    query = state.get("user_query", "")
    answer = state.get("final_answer", "")
    
    # Simple entity extraction (name, location, etc.)
    entities = state.get("entities", {})
    
    # Check for name patterns
    if "my name is" in query.lower():
        name = query.lower().split("my name is")[-1].strip().split()[0]
        entities["user_name"] = name.title()
    
    # Check for location patterns
    if "i live in" in query.lower():
        location = query.lower().split("i live in")[-1].strip().split()[0]
        entities["user_location"] = location.title()
    
    if entities != state.get("entities", {}):
        sys_msg = SystemMessage(content=f"Remembered: {', '.join(entities.keys())}")
        return {
            "messages": [sys_msg],
            "entities": entities,
        }
    
    return state


def update_memory_node(state: AdvancedAgentState) -> AdvancedAgentState:
    """Update and save conversation memory."""
    session_id = state.get("session_id", "default")
    message_count = state.get("message_count", 0) + 1
    
    # Save memory
    memory_data = {
        "summary": state.get("conversation_summary", ""),
        "entities": state.get("entities", {}),
        "message_count": message_count,
    }
    
    save_session_memory(session_id, memory_data)
    
    return {
        "message_count": message_count,
    }


def should_continue_react(state: AdvancedAgentState) -> Literal["react_action", "extract_entities"]:
    """Decide if ReAct should continue or finalize."""
    if state.get("final_answer"):
        return "extract_entities"
    if state.get("iteration", 0) >= state.get("max_iterations", 5):
        return "extract_entities"
    return "react_action"


def route_by_mode(state: AdvancedAgentState) -> Literal["simple_response", "react_reasoning"]:
    """Route based on selected mode."""
    return "react_reasoning" if state.get("mode") == "react" else "simple_response"


def build_advanced_agent():
    """Build the advanced agent with memory + ReAct."""
    graph = StateGraph(AdvancedAgentState)
    
    # Add nodes
    graph.add_node("initialize", initialize_node)
    graph.add_node("route_decision", route_decision_node)
    graph.add_node("simple_response", simple_response_node)
    graph.add_node("react_reasoning", react_reasoning_node)
    graph.add_node("react_action", react_action_node)
    graph.add_node("extract_entities", extract_entities_node)
    graph.add_node("update_memory", update_memory_node)
    
    # Build flow
    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "route_decision")
    
    # Route to simple or react
    graph.add_conditional_edges(
        "route_decision",
        route_by_mode,
        {
            "simple_response": "simple_response",
            "react_reasoning": "react_reasoning",
        }
    )
    
    # Simple path
    graph.add_edge("simple_response", "extract_entities")
    
    # ReAct loop
    graph.add_conditional_edges(
        "react_reasoning",
        should_continue_react,
        {
            "react_action": "react_action",
            "extract_entities": "extract_entities",
        }
    )
    graph.add_edge("react_action", "react_reasoning")
    
    # Both paths converge
    graph.add_edge("extract_entities", "update_memory")
    graph.add_edge("update_memory", END)
    
    return graph.compile()


def print_advanced_trace(state: AdvancedAgentState):
    """Print detailed trace."""
    print("\n" + "="*70)
    print("ADVANCED AGENT TRACE")
    print("="*70)
    print(f"Session: {state.get('session_id', 'N/A')}")
    print(f"Mode: {state.get('mode', 'N/A').upper()}")
    print(f"Query: {state.get('user_query', 'N/A')}")
    
    entities = state.get("entities", {})
    if entities:
        print(f"\nMemory - Entities: {entities}")
    
    print("\n" + "-"*70)
    print("EXECUTION TRACE:")
    print("-"*70)
    
    for msg in state.get("messages", []):
        if isinstance(msg, SystemMessage):
            print(f"💭 {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"🔧 {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"🤖 {msg.content}")
    
    print("\n" + "="*70)
    print(f"ANSWER: {state.get('final_answer', 'N/A')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Agent (Memory + ReAct)")
    parser.add_argument("--query", "-q", required=True, help="Your question/task")
    parser.add_argument("--session-id", default=str(uuid.uuid4()), help="Session ID")
    parser.add_argument("--mode", choices=["simple", "react", "auto"], default="auto",
                       help="Response mode (auto detects)")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max ReAct iterations")
    parser.add_argument("--visualize", action="store_true", help="Show graph")
    args = parser.parse_args()
    
    # Build agent
    agent = build_advanced_agent()
    
    # Visualize
    if args.visualize:
        try:
            print("\n📊 Advanced Agent Graph:\n")
            print(agent.get_graph().draw_ascii())
        except Exception as e:
            print(f"Visualization error: {e}")
    
    # Run
    initial_state = AdvancedAgentState(
        messages=[HumanMessage(content=args.query)],
        user_query=args.query,
        session_id=args.session_id,
        conversation_summary="",
        entities={},
        message_count=0,
        thought="",
        action="",
        action_input="",
        observation="",
        final_answer="",
        iteration=0,
        max_iterations=args.max_iterations,
        mode=args.mode,
    )
    
    print(f"\n🚀 Advanced Agent Processing...")
    print(f"Session: {args.session_id}")
    result = agent.invoke(initial_state)
    
    print_advanced_trace(result)
    
    print(f"\n💡 Continue this session: --session-id {args.session_id}")
