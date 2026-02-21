"""
Enhanced FastAPI Chatbot with Message History Tracking

This extends the existing chatbot API with:
- Full message history tracking (SystemMessage, HumanMessage, AIMessage)
- Conversation state persistence
- Message visualization endpoints
- WebSocket support with message streaming

Run:
    uvicorn langchain1.integrated_api:app --reload --port 8002

Endpoints:
    POST /chat - Send a message and get response with message history
    GET /chat/{session_id}/history - Get full message history for a session
    WS /ws/chat - WebSocket chat with real-time message streaming
    GET /visualize - Get graph visualization
"""
from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime
import json
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage

from .integrated_chatbot import build_integrated_chatbot, ConversationState

app = FastAPI(title="Integrated LangGraph Chatbot", version="1.0.0")

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, ConversationState] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    reingest: bool = False
    top_k: int = 4


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[str]
    route: str
    message_count: int
    timestamp: str


class MessageHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]
    total_messages: int


@app.get("/")
async def root():
    """API documentation."""
    return HTMLResponse("""
    <html>
        <head><title>Integrated LangGraph Chatbot</title></head>
        <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: auto;">
            <h1>🤖 Integrated LangGraph Chatbot API</h1>
            <p>This API combines RAG and Weather capabilities with full message history tracking.</p>
            
            <h2>Features</h2>
            <ul>
                <li>✅ SystemMessage, HumanMessage, AIMessage tracking</li>
                <li>✅ Session-based conversation history</li>
                <li>✅ RAG (Retrieval-Augmented Generation)</li>
                <li>✅ Real-time weather data</li>
                <li>✅ WebSocket support</li>
                <li>✅ Graph visualization</li>
            </ul>
            
            <h2>Endpoints</h2>
            <ul>
                <li><code>POST /chat</code> - Send a message</li>
                <li><code>GET /chat/{session_id}/history</code> - Get message history</li>
                <li><code>GET /sessions</code> - List all sessions</li>
                <li><code>DELETE /sessions/{session_id}</code> - Delete a session</li>
                <li><code>GET /visualize</code> - Get graph visualization</li>
                <li><code>WS /ws/chat</code> - WebSocket chat</li>
            </ul>
            
            <h2>Quick Test</h2>
            <p>Try: <code>curl -X POST http://localhost:8002/chat -H "Content-Type: application/json" -d '{"message": "What is RAG?"}'</code></p>
            
            <p><a href="/docs">📖 Interactive API Docs (Swagger)</a></p>
        </body>
    </html>
    """)


@app.get("/health")
async def health():
    return {"status": "ok", "sessions": len(sessions)}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Send a message to the chatbot.
    
    - Creates a new session if session_id not provided
    - Maintains conversation history
    - Routes to weather or RAG based on intent
    """
    # Get or create session
    session_id = req.session_id or str(uuid.uuid4())
    
    if session_id in sessions:
        # Continue existing conversation
        state = sessions[session_id]
        # Add new human message
        new_messages = list(state.get("messages", []))
        new_messages.append(HumanMessage(content=req.message))
        state["messages"] = new_messages
        state["user_query"] = req.message
        state["reingest"] = req.reingest
        state["top_k"] = req.top_k
    else:
        # New conversation
        state = ConversationState(
            messages=[HumanMessage(content=req.message)],
            route="",
            user_query=req.message,
            answer="",
            sources=[],
            reingest=req.reingest,
            top_k=req.top_k,
        )
    
    # Run the graph
    chatbot = build_integrated_chatbot()
    result = chatbot.invoke(state)
    
    # Store updated state
    sessions[session_id] = result
    
    return ChatResponse(
        session_id=session_id,
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        route=result.get("route", "unknown"),
        message_count=len(result.get("messages", [])),
        timestamp=datetime.now().isoformat(),
    )


@app.get("/chat/{session_id}/history", response_model=MessageHistoryResponse)
async def get_history(session_id: str):
    """Get full message history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    messages = state.get("messages", [])
    
    # Convert messages to serializable format
    msg_list = []
    for msg in messages:
        msg_list.append({
            "type": type(msg).__name__,
            "content": msg.content,
            "timestamp": datetime.now().isoformat(),
        })
    
    return MessageHistoryResponse(
        session_id=session_id,
        messages=msg_list,
        total_messages=len(msg_list),
    )


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(state.get("messages", [])),
                "route": state.get("route", "unknown"),
            }
            for sid, state in sessions.items()
        ]
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/visualize")
async def visualize_graph():
    """Get ASCII visualization of the graph structure."""
    chatbot = build_integrated_chatbot()
    try:
        ascii_graph = chatbot.get_graph().draw_ascii()
        return {"graph": ascii_graph, "format": "ascii"}
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket chat endpoint with message streaming.
    
    Client sends: {"message": "...", "session_id": "...", "reingest": false, "top_k": 4}
    Server sends: {"type": "message", "content": {...}}
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue
            
            message = payload.get("message")
            if not message:
                await websocket.send_json({"error": "Missing 'message' field"})
                continue
            
            session_id = payload.get("session_id", session_id)
            reingest = payload.get("reingest", False)
            top_k = payload.get("top_k", 4)
            
            # Build state
            if session_id in sessions:
                state = sessions[session_id]
                new_messages = list(state.get("messages", []))
                new_messages.append(HumanMessage(content=message))
                state["messages"] = new_messages
                state["user_query"] = message
                state["reingest"] = reingest
                state["top_k"] = top_k
            else:
                state = ConversationState(
                    messages=[HumanMessage(content=message)],
                    route="",
                    user_query=message,
                    answer="",
                    sources=[],
                    reingest=reingest,
                    top_k=top_k,
                )
            
            # Send processing status
            await websocket.send_json({
                "type": "status",
                "content": "Processing your message..."
            })
            
            # Run graph
            chatbot = build_integrated_chatbot()
            result = chatbot.invoke(state)
            sessions[session_id] = result
            
            # Send each message in the result
            for msg in result.get("messages", []):
                await websocket.send_json({
                    "type": "message",
                    "message_type": type(msg).__name__,
                    "content": msg.content,
                })
            
            # Send final response
            await websocket.send_json({
                "type": "response",
                "session_id": session_id,
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "route": result.get("route", ""),
                "done": True,
            })
            
    except WebSocketDisconnect:
        if session_id in sessions:
            # Optionally clean up session on disconnect
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
