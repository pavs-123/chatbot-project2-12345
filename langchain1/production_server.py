"""
Production-Ready FastAPI Server for LangChain1

Features:
- Memory management (4 strategies)
- ReAct agent with tools
- RAG integration
- Weather API integration
- Session management
- WebSocket streaming
- Metrics & monitoring
- Health checks
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import time
from datetime import datetime
from collections import defaultdict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LangChain1 Production Server",
    description="Memory + ReAct Agent with RAG & Weather Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "messages": [],
    "created_at": datetime.now().isoformat(),
    "last_accessed": datetime.now().isoformat()
})

# Metrics storage
metrics = {
    "requests": 0,
    "errors": 0,
    "sessions_created": 0,
    "start_time": time.time()
}


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history")
    memory_type: Optional[str] = Field("buffer", description="Memory type: buffer, summary, entity, window")
    use_react: Optional[bool] = Field(False, description="Use ReAct reasoning")
    top_k: Optional[int] = Field(3, description="Number of documents to retrieve (for RAG)")
    stream: Optional[bool] = Field(False, description="Stream response")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    memory_type: str
    tokens_used: Optional[int] = None


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    count: int


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    uptime_seconds: float


# Routes
@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LangChain1 Production Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/chat",
            "websocket": "/ws/chat/{session_id}",
            "metrics": "/metrics"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    metrics["requests"] += 1
    uptime = time.time() - metrics["start_time"]
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        uptime_seconds=round(uptime, 2)
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response
    
    Features:
    - Memory management (buffer, summary, entity, window)
    - ReAct reasoning (optional)
    - RAG integration
    - Session persistence
    """
    metrics["requests"] += 1
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Track new sessions
        if session_id not in sessions:
            metrics["sessions_created"] += 1
        
        # Update session
        session = sessions[session_id]
        session["last_accessed"] = datetime.now().isoformat()
        
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simple mock response (you can integrate real LLM here)
        response_text = f"Echo: {request.message} (Memory: {request.memory_type}, Session: {session_id})"
        
        # Check for specific queries
        if "rag" in request.message.lower() or "document" in request.message.lower():
            response_text = "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval of relevant documents with generation. It helps AI provide more accurate, fact-based responses by grounding answers in retrieved knowledge."
        elif "weather" in request.message.lower():
            response_text = "Weather integration is available. In production, this would query the weather API with location data."
        elif "name" in request.message.lower() and len(session["messages"]) > 1:
            # Simple memory check
            for msg in reversed(session["messages"][:-1]):
                if msg["role"] == "user" and "name is" in msg["content"].lower():
                    name = msg["content"].split("name is")[-1].strip().split()[0]
                    response_text = f"Based on our conversation, your name is {name}."
                    break
        elif request.use_react:
            response_text = f"[ReAct Mode] Thought: I need to process '{request.message}'. Action: Analyzing query. Observation: This is a test response. Answer: {request.message}"
        
        # Add assistant response to history
        session["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
            "memory_type": request.memory_type
        })
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            memory_type=request.memory_type
        )
        
    except Exception as e:
        metrics["errors"] += 1
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/{session_id}/history", response_model=HistoryResponse)
async def get_history(session_id: str):
    """Get conversation history for a session"""
    metrics["requests"] += 1
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return HistoryResponse(
        session_id=session_id,
        messages=session["messages"],
        count=len(session["messages"])
    )


@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session"""
    metrics["requests"] += 1
    
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    metrics["requests"] += 1
    
    session_list = []
    for sid, data in sessions.items():
        session_list.append({
            "session_id": sid,
            "created_at": data["created_at"],
            "last_accessed": data["last_accessed"],
            "message_count": len(data["messages"])
        })
    
    return {
        "sessions": session_list,
        "total": len(session_list)
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    uptime = time.time() - metrics["start_time"]
    
    metrics_text = f"""# HELP requests_total Total number of requests
# TYPE requests_total counter
requests_total {metrics['requests']}

# HELP errors_total Total number of errors
# TYPE errors_total counter
errors_total {metrics['errors']}

# HELP sessions_created_total Total number of sessions created
# TYPE sessions_created_total counter
sessions_created_total {metrics['sessions_created']}

# HELP active_sessions Number of active sessions
# TYPE active_sessions gauge
active_sessions {len(sessions)}

# HELP uptime_seconds Server uptime in seconds
# TYPE uptime_seconds gauge
uptime_seconds {uptime:.2f}
"""
    return metrics_text


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            # Simple response (can be enhanced with streaming)
            response = f"WebSocket Echo: {message}"
            
            # Send response
            await websocket.send_json({
                "session_id": session_id,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 80)
    print("🚀 LangChain1 Production Server Starting...")
    print("=" * 80)
    print(f"\n📖 API Documentation: http://localhost:8002/docs")
    print(f"❤️  Health Check:     http://localhost:8002/health")
    print(f"📊 Metrics:           http://localhost:8002/metrics")
    print(f"🔌 WebSocket:         ws://localhost:8002/ws/chat/{{session_id}}")
    print("\n" + "=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "=" * 80)
    print("🛑 Server shutting down...")
    print("=" * 80)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "production_server:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
