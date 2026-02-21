"""
ReAct Agent with LangGraph

ReAct = Reasoning + Acting
The agent reasons about what to do, then acts using tools.

Tools available:
1. Calculator - Perform math calculations
2. Search (RAG) - Search knowledge base
3. Weather - Get weather information
4. Python REPL - Execute Python code

Usage:
    python langchain1/react_agent.py --query "What is 25 * 47?"
    python langchain1/react_agent.py --query "What's the weather in Paris and multiply the temperature by 2"
"""
from __future__ import annotations
from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Literal
import operator
import re
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chatbot.llm_provider import get_llm

# For tools
from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain
from mcp_weather import helpers as weather_helpers
import anyio


# Define tools
@tool
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations. 
    
    Args:
        expression: A mathematical expression like "25 * 47" or "(100 + 50) / 2"
    
    Returns:
        The result of the calculation
    """
    try:
        # Safe eval with limited scope
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error in calculation: {e}"


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the knowledge base (RAG) for information.
    
    Args:
        query: The search query
    
    Returns:
        Relevant information from the knowledge base
    """
    try:
        from chatbot.llm_provider import get_llm, get_embeddings
        
        cfg = RAGConfig()
        cfg.ensure_dirs()
        embeddings = get_embeddings()
        vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, False, embeddings)
        retriever = get_retriever(vectorstore, k=3)
        llm = get_llm()
        chain = build_rag_chain(retriever, llm)
        
        answer = chain.invoke(query)
        return f"Knowledge Base: {answer}"
    except Exception as e:
        return f"Error searching knowledge base: {e}"


@tool
def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    
    Args:
        city: Name of the city
    
    Returns:
        Weather information
    """
    try:
        async def _fetch(city: str):
            info = await weather_helpers.geocode_city(city)
            if not info:
                return f"Could not find city '{city}'"
            data = await weather_helpers.fetch_weather(info["latitude"], info["longitude"])
            current = data.get("current_weather", data)
            temp = current.get("temperature")
            wind = current.get("windspeed")
            return f"Weather in {info.get('name', city)}: {temp}°C, wind {wind} km/h"
        
        result = anyio.run(_fetch, city)
        return result
    except Exception as e:
        return f"Error getting weather: {e}"


@tool
def python_repl(code: str) -> str:
    """
    Execute Python code safely.
    
    Args:
        code: Python code to execute
    
    Returns:
        Output of the code execution
    """
    try:
        # Very restricted execution environment
        import io
        import contextlib
        
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            # Only allow basic operations
            allowed_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                }
            }
            exec(code, allowed_globals)
        
        return output.getvalue() or "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing code: {e}"


# Tool registry
TOOLS = {
    "calculator": calculator,
    "search_knowledge_base": search_knowledge_base,
    "get_weather": get_weather,
    "python_repl": python_repl,
}


class ReActState(TypedDict):
    """State for ReAct agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    thought: str
    action: str
    action_input: str
    observation: str
    final_answer: str
    iteration: int
    max_iterations: int


def reasoning_node(state: ReActState) -> ReActState:
    """
    Reasoning step: Think about what to do next.
    Uses the ReAct pattern: Thought -> Action -> Observation
    """
    query = state.get("user_query", "")
    messages = state.get("messages", [])
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 5)
    
    # Check if we should stop
    if iteration >= max_iterations:
        return {
            "final_answer": "Maximum iterations reached. Unable to complete task.",
            "iteration": iteration,
        }
    
    # Build reasoning prompt
    tools_desc = "\n".join([
        f"- {name}: {tool.description}"
        for name, tool in TOOLS.items()
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a ReAct agent. Follow this pattern:\n"
         "Thought: Think about what to do\n"
         "Action: Choose a tool to use\n"
         "Action Input: Input for the tool\n\n"
         "Available tools:\n{tools}\n\n"
         "If you have enough information to answer, use:\n"
         "Thought: I have enough information\n"
         "Final Answer: Your answer\n\n"
         "IMPORTANT: Always output your response in this exact format."),
        ("human", "Question: {query}\n\nPrevious observations:\n{history}\n\nWhat do you do next?")
    ])
    
    # Get history of observations
    history = "\n".join([
        msg.content for msg in messages 
        if isinstance(msg, (SystemMessage, ToolMessage))
    ][-5:])  # Last 5 observations
    
    llm = get_llm()
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "query": query,
            "tools": tools_desc,
            "history": history or "None yet"
        })
        response = result.content if hasattr(result, 'content') else str(result)
        
        # Parse response
        thought = ""
        action = ""
        action_input = ""
        final_answer = ""
        
        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
            thought = response.split("Thought:")[-1].split("Final Answer:")[0].strip()
        else:
            if "Thought:" in response:
                thought = response.split("Thought:")[-1].split("Action:")[0].strip()
            if "Action:" in response:
                action = response.split("Action:")[-1].split("Action Input:")[0].strip()
            if "Action Input:" in response:
                action_input = response.split("Action Input:")[-1].strip()
        
        sys_msg = SystemMessage(content=f"[Iteration {iteration + 1}] Thought: {thought}")
        
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
            "final_answer": f"Error in reasoning: {e}",
            "iteration": iteration + 1,
        }


def action_node(state: ReActState) -> ReActState:
    """
    Action step: Execute the chosen tool.
    """
    action = state.get("action", "").lower().replace(" ", "_")
    action_input = state.get("action_input", "")
    
    if not action or action not in TOOLS:
        observation = f"Invalid action '{action}'. Available: {', '.join(TOOLS.keys())}"
    else:
        try:
            tool = TOOLS[action]
            observation = tool.invoke(action_input)
        except Exception as e:
            observation = f"Error executing {action}: {e}"
    
    tool_msg = ToolMessage(content=f"Observation: {observation}", tool_call_id=action)
    
    return {
        "messages": [tool_msg],
        "observation": observation,
    }


def should_continue(state: ReActState) -> Literal["action", "finalize"]:
    """Decide whether to continue or finalize."""
    if state.get("final_answer"):
        return "finalize"
    if state.get("iteration", 0) >= state.get("max_iterations", 5):
        return "finalize"
    return "action"


def finalize_node(state: ReActState) -> ReActState:
    """Finalize and return the answer."""
    final_answer = state.get("final_answer", "Unable to determine answer.")
    
    ai_msg = AIMessage(content=final_answer)
    
    return {
        "messages": [ai_msg],
        "final_answer": final_answer,
    }


def build_react_agent():
    """Build ReAct agent graph."""
    graph = StateGraph(ReActState)
    
    # Add nodes
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("action", action_node)
    graph.add_node("finalize", finalize_node)
    
    # Build flow
    graph.set_entry_point("reasoning")
    
    # Conditional edge: reasoning -> action or finalize
    graph.add_conditional_edges(
        "reasoning",
        should_continue,
        {
            "action": "action",
            "finalize": "finalize",
        }
    )
    
    # Action loops back to reasoning
    graph.add_edge("action", "reasoning")
    
    # Finalize goes to END
    graph.add_edge("finalize", END)
    
    return graph.compile()


def print_react_trace(state: ReActState):
    """Print the ReAct reasoning trace."""
    print("\n" + "="*70)
    print("REACT AGENT TRACE")
    print("="*70)
    
    print(f"Query: {state.get('user_query', 'N/A')}")
    print(f"Iterations: {state.get('iteration', 0)}")
    
    print("\n" + "-"*70)
    print("REASONING TRACE:")
    print("-"*70)
    
    for msg in state.get("messages", []):
        if isinstance(msg, SystemMessage):
            print(f"\n💭 {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"🔧 {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"\n✅ FINAL: {msg.content}")
    
    print("\n" + "="*70)
    print(f"Answer: {state.get('final_answer', 'N/A')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ReAct Agent")
    parser.add_argument("--query", "-q", required=True, help="Your question/task")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum iterations")
    parser.add_argument("--visualize", action="store_true", help="Show graph")
    args = parser.parse_args()
    
    # Build agent
    agent = build_react_agent()
    
    # Visualize
    if args.visualize:
        try:
            print("\n📊 ReAct Agent Graph:\n")
            print(agent.get_graph().draw_ascii())
        except Exception as e:
            print(f"Could not visualize: {e}")
    
    # Create initial state
    initial_state = ReActState(
        messages=[HumanMessage(content=args.query)],
        user_query=args.query,
        thought="",
        action="",
        action_input="",
        observation="",
        final_answer="",
        iteration=0,
        max_iterations=args.max_iterations,
    )
    
    # Run
    print(f"\n🤖 ReAct Agent processing: '{args.query}'")
    result = agent.invoke(initial_state)
    
    # Print trace
    print_react_trace(result)
