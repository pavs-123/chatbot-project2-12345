"""
Chatbot FastAPI built on the existing RAG pipeline.

Run:
  uvicorn chatbot.api:app --reload --port 8001

POST /chat
  Body: {"message": "...", "reingest": false, "top_k": 4}
  Returns: {"answer": "...", "sources": ["path1", "path2", ...]}
"""
from __future__ import annotations
from typing import Any, List, Optional
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from pathlib import Path

from rag.config import RAGConfig
from rag.ingest import build_or_load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from .graph import build_chat_flow
from .memory import get_memory_manager

app = FastAPI(title="Chatbot (RAG)", version="0.2.0")

# CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# User upload directory
upload_dir = Path("chatbot/uploads")
upload_dir.mkdir(parents=True, exist_ok=True)


class ChatRequest(BaseModel):
    message: str
    reingest: bool = False
    top_k: Optional[int] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    session_id: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]


@app.get("/")
async def root():
    """Serve the HTML UI"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Chatbot API - use /chat, /chat/stream, or /ws/chat"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to be added to the RAG knowledge base"""
    try:
        # Save uploaded file
        file_path = upload_dir / file.filename
        content = await file.read()
        file_path.write_bytes(content)
        
        # Copy to RAG docs directory
        cfg = RAGConfig()
        cfg.ensure_dirs()
        rag_file_path = cfg.docs_dir / file.filename
        rag_file_path.write_bytes(content)
        
        return JSONResponse({
            "status": "success",
            "message": f"Uploaded {file.filename}. Use reingest=true in your next chat to index it.",
            "filename": file.filename
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """Get conversation history for a session"""
    memory_mgr = get_memory_manager()
    memory = memory_mgr.get_or_create(session_id)
    
    return HistoryResponse(
        session_id=session_id,
        messages=memory.get_messages()
    )


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    memory_mgr = get_memory_manager()
    memory = memory_mgr.get_or_create(session_id)
    memory.clear()
    memory_mgr.save_session(session_id)
    
    return {"status": "success", "message": f"Cleared history for session {session_id}"}


@app.get("/sessions")
async def list_sessions():
    """List all saved sessions"""
    memory_mgr = get_memory_manager()
    return {"sessions": memory_mgr.list_sessions()}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    # Get or create session
    memory_mgr = get_memory_manager()
    session_id = req.session_id or str(uuid.uuid4())
    memory = memory_mgr.get_or_create(session_id)
    
    # Add user message to history
    memory.add_message("user", req.message)
    
    # Get conversation context
    chat_history = memory.get_context(last_n=5)
    
    # Use LangGraph flow for orchestration (intent + route + answer)
    flow = build_chat_flow()
    out = flow.invoke({
        "message": req.message,
        "reingest": req.reingest,
        "top_k": req.top_k or 0,
        "session_id": session_id,
        "chat_history": chat_history,
    })
    
    answer = out.get("answer", "")
    
    # Add assistant response to history
    memory.add_message("assistant", answer)
    
    # Save session periodically
    memory_mgr.save_session(session_id)
    
    return ChatResponse(
        answer=answer,
        sources=out.get("sources", []),
        session_id=session_id
    )


@app.get("/chat/stream")
async def chat_stream(message: str, reingest: bool = False, top_k: int | None = None):
    """Server-Sent Events (SSE) streaming of the chatbot answer.

    This uses chunked responses to simulate streaming by splitting the
    final answer into pieces. For true token streaming, you can use an LLM
    that supports streaming callbacks and yield chunks as they arrive.
    """
    cfg = RAGConfig()
    cfg.ensure_dirs()

    embeddings = OpenAIEmbeddings(model=cfg.embedding_model)
    vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, reingest, embeddings)

    k = top_k if top_k is not None else cfg.top_k
    retriever = get_retriever(vectorstore, k=k)
    llm = ChatOpenAI(model=cfg.chat_model, temperature=0)
    chain = build_rag_chain(retriever, llm)

    answer: str = chain.invoke(message)

    async def sse_gen():
        # Basic split into ~50-char chunks for demo streaming
        chunk_size = 60
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i:i+chunk_size]
            event = f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield event
            await asyncio.sleep(0.02)
        # Send done event
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(sse_gen(), media_type="text/event-stream")


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    """WebSocket chat endpoint.

    Client sends JSON messages like:
      {"message": "your text", "reingest": false, "top_k": 4}

    Server replies with JSON frames streaming the answer chunks and finally
    a {"done": true, "sources": [...]} frame.
    """
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            try:
                payload = json.loads(data)
            except Exception:
                await ws.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            message = payload.get("message")
            if not message:
                await ws.send_text(json.dumps({"error": "Missing 'message'"}))
                continue

            reingest = bool(payload.get("reingest", False))
            top_k = payload.get("top_k")

            # Build pipeline
            cfg = RAGConfig(); cfg.ensure_dirs()
            embeddings = OpenAIEmbeddings(model=cfg.embedding_model)
            vectorstore = build_or_load_vectorstore(cfg.docs_dir, cfg.persist_dir, reingest, embeddings)
            k = int(top_k) if top_k is not None else cfg.top_k
            retriever = get_retriever(vectorstore, k=k)
            llm = ChatOpenAI(model=cfg.chat_model, temperature=0)
            chain = build_rag_chain(retriever, llm)

            # Produce full answer, then stream in chunks to simplify
            answer: str = chain.invoke(message)
            chunk_size = 60
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i+chunk_size]
                await ws.send_text(json.dumps({"chunk": chunk}))
                await asyncio.sleep(0.02)

            # Send sources at the end
            try:
                docs = retriever.invoke(message)
                sources = []
                for d in docs[:k]:
                    src = (getattr(d, "metadata", {}) or {}).get("source") or "unknown"
                    if src not in sources:
                        sources.append(src)
            except Exception:
                sources = []

            await ws.send_text(json.dumps({"done": True, "sources": sources}))
    except WebSocketDisconnect:
        return
