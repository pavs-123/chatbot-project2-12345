"""
LangGraph flow to orchestrate multi-step chat responses.

Nodes:
- detect_intent: classify message into {weather, rag}
- handle_weather: if weather intent -> call Open‑Meteo helpers and format
- handle_rag: if rag intent -> run RAG pipeline (retriever + LLM)
- finalize: ensure answer/sources exist

Usage:
  from chatbot.graph import build_chat_flow
  graph = build_chat_flow()
  out = graph.invoke({"message": "What is RAG?"})
"""
from __future__ import annotations
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, END

# Reuse existing RAG components
from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain
from .llm_provider import get_llm, get_embeddings

# Weather helpers (async). We'll call them via anyio to keep nodes sync-friendly.
# Use weather helpers directly for simplicity
from mcp_weather import helpers as weather_helpers
import anyio


class ChatState(TypedDict, total=False):
    message: str
    route: str  # "weather" | "rag"
    answer: str
    sources: List[str]
    # Configurable knobs
    reingest: bool
    top_k: int
    # Memory support
    session_id: str
    chat_history: str  # Recent conversation context


def detect_intent(state: ChatState) -> ChatState:
    msg = (state.get("message") or "").lower()
    if any(k in msg for k in ["weather", "forecast", "temperature", "rain", "wind", "humidity"]):
        state["route"] = "weather"
    else:
        state["route"] = "rag"
    return state


def handle_weather(state: ChatState) -> ChatState:
    """Handle weather requests by extracting a simple city heuristic and calling helpers."""
    msg = state.get("message", "")
    # naive heuristic: last word capitalized or after "in "; fall back to whole msg
    city: Optional[str] = None
    for token in msg.replace("?", "").split():
        if token.lower() == "in":
            # next token might be city
            continue
    # Try to find "in CITY" pattern
    parts = msg.split(" in ")
    if len(parts) > 1:
        candidate = parts[-1].strip().strip(".?!,")
        if candidate:
            city = candidate
    if not city:
        # fallback: first capitalized token
        for t in msg.split():
            if t[:1].isupper():
                city = t
                break
    if not city:
        # fallback to entire message (geocoder is robust for city names)
        city = msg.strip()

    async def _call(city: str) -> Dict[str, Any]:
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
        state["answer"] = result["error"]
        state["sources"] = []
        return state

    cur = result["current"]
    temp = cur.get("temperature")
    wind = cur.get("windspeed")
    code = cur.get("weathercode")
    city_name = result["city"]
    state["answer"] = f"Weather in {city_name}: temperature {temp}°C, wind {wind} km/h (code {code})."
    state["sources"] = ["open-meteo"]
    return state


def handle_rag(state: ChatState) -> ChatState:
    cfg = RAGConfig(); cfg.ensure_dirs()
    embeddings = get_embeddings()
    vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, bool(state.get("reingest", False)), embeddings)

    k = int(state.get("top_k", cfg.top_k))
    retriever = get_retriever(vectorstore, k=k)
    llm = get_llm()
    chain = build_rag_chain(retriever, llm, chat_history=state.get("chat_history"))

    q = state.get("message", "")
    answer: str = chain.invoke(q)
    state["answer"] = answer

    try:
        docs = retriever.invoke(q)
        sources: List[str] = []
        for d in docs[:k]:
            src = (getattr(d, "metadata", {}) or {}).get("source") or "unknown"
            if src not in sources:
                sources.append(src)
        state["sources"] = sources
    except Exception:
        state["sources"] = []

    return state


def router(state: ChatState) -> str:
    return state.get("route", "rag")


def finalize(state: ChatState) -> ChatState:
    state.setdefault("answer", "I'm not sure how to help with that.")
    state.setdefault("sources", [])
    return state


def build_chat_flow():
    g = StateGraph(ChatState)
    g.add_node("detect_intent", detect_intent)
    g.add_node("handle_weather", handle_weather)
    g.add_node("handle_rag", handle_rag)
    g.add_node("finalize", finalize)

    g.set_entry_point("detect_intent")
    # Conditional routing after intent
    g.add_conditional_edges("detect_intent", router, {
        "weather": "handle_weather",
        "rag": "handle_rag",
    })
    # Both branches go to finalize then END
    g.add_edge("handle_weather", "finalize")
    g.add_edge("handle_rag", "finalize")
    g.add_edge("finalize", END)

    return g.compile()
