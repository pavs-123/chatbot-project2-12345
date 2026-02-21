"""
Integrated LangGraph Chatbot with SystemMessage and HumanMessage
Combines the existing chatbot/RAG system with explicit message types.

This demonstrates how to:
1. Use SystemMessage to set context for each route (weather/RAG)
2. Use HumanMessage for user queries
3. Use AIMessage for responses
4. Track conversation history with proper message types
5. Visualize the message flow through the graph
"""
from __future__ import annotations
from typing import TypedDict, List, Annotated, Sequence
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

# Reuse existing components
from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chatbot.llm_provider import get_llm, get_embeddings

# Weather helpers
from mcp_weather import helpers as weather_helpers
import anyio


class ConversationState(TypedDict):
    """State with message history tracking."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    route: str  # "weather" | "rag"
    user_query: str  # Original user text
    answer: str
    sources: List[str]
    # Config
    reingest: bool
    top_k: int


def detect_intent_node(state: ConversationState) -> ConversationState:
    """
    Detect user intent and add a SystemMessage explaining the routing decision.
    """
    # Get the last human message
    messages = state.get("messages", [])
    user_msg = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_msg = msg.content
            break
    
    if not user_msg:
        user_msg = state.get("user_query", "")
    
    # Detect intent
    msg_lower = user_msg.lower()
    if any(k in msg_lower for k in ["weather", "forecast", "temperature", "rain", "wind", "humidity"]):
        route = "weather"
        system_msg = SystemMessage(
            content="Intent detected: WEATHER query. I will fetch real-time weather data from Open-Meteo."
        )
    else:
        route = "rag"
        system_msg = SystemMessage(
            content="Intent detected: RAG query. I will search my knowledge base and provide a contextual answer."
        )
    
    return {
        "messages": [system_msg],
        "route": route,
        "user_query": user_msg,
        "answer": state.get("answer", ""),
        "sources": state.get("sources", []),
        "reingest": state.get("reingest", False),
        "top_k": state.get("top_k", 4),
    }


def weather_node(state: ConversationState) -> ConversationState:
    """
    Handle weather requests with SystemMessage context.
    """
    query = state.get("user_query", "")
    
    # Add system message about weather processing
    sys_msg = SystemMessage(
        content="Processing weather request. Geocoding location and fetching current conditions..."
    )
    
    # Extract city (reuse logic from original chatbot)
    city: str | None = None
    parts = query.split(" in ")
    if len(parts) > 1:
        candidate = parts[-1].strip().strip(".?!,")
        if candidate:
            city = candidate
    if not city:
        for t in query.split():
            if t and t[0].isupper():
                city = t
                break
    if not city:
        city = query.strip()
    
    # Fetch weather data
    async def _call(city: str):
        info = await weather_helpers.geocode_city(city)
        if not info:
            return {"error": f"Could not find city '{city}'"}
        data = await weather_helpers.fetch_weather(info["latitude"], info["longitude"])
        current = data.get("current_weather", data)
        return {
            "city": info.get("name", city),
            "coords": {"lat": info.get("latitude"), "lon": info.get("longitude")},
            "current": current,
        }
    
    result = anyio.run(_call, city)
    
    if "error" in result:
        ai_msg = AIMessage(content=result["error"])
        answer = result["error"]
        sources = []
    else:
        cur = result["current"]
        temp = cur.get("temperature")
        wind = cur.get("windspeed")
        code = cur.get("weathercode")
        city_name = result["city"]
        
        answer = f"Weather in {city_name}: temperature {temp}°C, wind {wind} km/h (weather code {code})."
        ai_msg = AIMessage(content=answer)
        sources = ["open-meteo"]
    
    return {
        "messages": [sys_msg, ai_msg],
        "route": state.get("route", "weather"),
        "user_query": query,
        "answer": answer,
        "sources": sources,
        "reingest": state.get("reingest", False),
        "top_k": state.get("top_k", 4),
    }


def rag_node(state: ConversationState) -> ConversationState:
    """
    Handle RAG requests with SystemMessage context.
    """
    query = state.get("user_query", "")
    
    # Add system message about RAG processing
    sys_msg = SystemMessage(
        content="Processing RAG query. Retrieving relevant documents and generating answer with LLM..."
    )
    
    # Build RAG pipeline
    cfg = RAGConfig()
    cfg.ensure_dirs()
    embeddings = get_embeddings()
    vectorstore = build_or_load_vectorstore(
        cfg.docs_dir, 
        cfg.persist_dir, 
        bool(state.get("reingest", False)), 
        embeddings
    )
    
    k = int(state.get("top_k", cfg.top_k))
    retriever = get_retriever(vectorstore, k=k)
    llm = get_llm()
    chain = build_rag_chain(retriever, llm)
    
    # Get answer
    answer: str = chain.invoke(query)
    
    # Get sources
    try:
        docs = retriever.invoke(query)
        sources: List[str] = []
        for d in docs[:k]:
            src = (getattr(d, "metadata", {}) or {}).get("source") or "unknown"
            if src not in sources:
                sources.append(src)
    except Exception:
        sources = []
    
    # Create AI message with the answer
    ai_msg = AIMessage(content=answer)
    
    return {
        "messages": [sys_msg, ai_msg],
        "route": state.get("route", "rag"),
        "user_query": query,
        "answer": answer,
        "sources": sources,
        "reingest": state.get("reingest", False),
        "top_k": state.get("top_k", k),
    }


def finalize_node(state: ConversationState) -> ConversationState:
    """
    Finalize response and ensure all fields are set.
    """
    # Add a final system message summarizing
    messages = state.get("messages", [])
    sources = state.get("sources", [])
    
    summary = SystemMessage(
        content=f"Response completed. Sources used: {', '.join(sources) if sources else 'None'}"
    )
    
    return {
        "messages": [summary],
        "route": state.get("route", ""),
        "user_query": state.get("user_query", ""),
        "answer": state.get("answer", "I'm not sure how to help with that."),
        "sources": sources,
        "reingest": state.get("reingest", False),
        "top_k": state.get("top_k", 4),
    }


def route_by_intent(state: ConversationState) -> str:
    """Router function for conditional edges."""
    return state.get("route", "rag")


def build_integrated_chatbot():
    """
    Build the integrated LangGraph chatbot with message types.
    
    Graph structure:
        START -> detect_intent -> [weather_node OR rag_node] -> finalize -> END
    
    Returns:
        Compiled LangGraph
    """
    graph = StateGraph(ConversationState)
    
    # Add nodes
    graph.add_node("detect_intent", detect_intent_node)
    graph.add_node("weather", weather_node)
    graph.add_node("rag", rag_node)
    graph.add_node("finalize", finalize_node)
    
    # Set entry point
    graph.set_entry_point("detect_intent")
    
    # Conditional routing after intent detection
    graph.add_conditional_edges(
        "detect_intent",
        route_by_intent,
        {
            "weather": "weather",
            "rag": "rag",
        }
    )
    
    # Both paths converge at finalize
    graph.add_edge("weather", "finalize")
    graph.add_edge("rag", "finalize")
    graph.add_edge("finalize", END)
    
    return graph.compile()


def print_message_history(state: ConversationState):
    """Pretty print the message history."""
    print("\n" + "="*60)
    print("MESSAGE HISTORY")
    print("="*60)
    
    for i, msg in enumerate(state.get("messages", []), 1):
        msg_type = type(msg).__name__
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"\n{i}. [{msg_type}]")
        print(f"   {content}")
    
    print("\n" + "="*60)
    print(f"Final Answer: {state.get('answer', 'N/A')}")
    print(f"Sources: {', '.join(state.get('sources', []))}")
    print("="*60 + "\n")


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated LangGraph Chatbot")
    parser.add_argument("--query", "-q", required=True, help="Your question")
    parser.add_argument("--reingest", action="store_true", help="Rebuild vector DB")
    parser.add_argument("--top-k", type=int, default=4, help="Number of docs to retrieve")
    parser.add_argument("--visualize", action="store_true", help="Show graph visualization")
    args = parser.parse_args()
    
    # Build the graph
    chatbot = build_integrated_chatbot()
    
    # Visualize if requested
    if args.visualize:
        try:
            print("\n📊 Graph Structure (ASCII):\n")
            print(chatbot.get_graph().draw_ascii())
        except Exception as e:
            print(f"Could not visualize: {e}")
    
    # Create initial state with HumanMessage
    initial_state = ConversationState(
        messages=[HumanMessage(content=args.query)],
        route="",
        user_query=args.query,
        answer="",
        sources=[],
        reingest=args.reingest,
        top_k=args.top_k,
    )
    
    # Run the graph
    print(f"\n🤖 Processing query: '{args.query}'")
    result = chatbot.invoke(initial_state)
    
    # Print the message history
    print_message_history(result)
