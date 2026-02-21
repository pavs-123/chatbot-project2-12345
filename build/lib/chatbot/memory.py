"""
Conversation Memory Management for Chatbot

Provides in-memory conversation history per session with automatic summarization.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class Message:
    """Single chat message"""
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationMemory:
    """Manages conversation history for a session"""
    
    def __init__(self, session_id: str, max_messages: int = 20):
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: List[Message] = []
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add a message to history"""
        msg = Message(role, content)
        self.messages.append(msg)
        
        # Keep only last N messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context(self, last_n: int = 5) -> str:
        """Get recent conversation context as formatted string"""
        recent = self.messages[-last_n:] if self.messages else []
        if not recent:
            return ""
        
        context_lines = ["Recent conversation:"]
        for msg in recent:
            context_lines.append(f"{msg.role.capitalize()}: {msg.content}")
        return "\n".join(context_lines)
    
    def get_messages(self) -> List[Dict]:
        """Get all messages as dict list"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self):
        """Clear conversation history"""
        self.messages.clear()
    
    def to_dict(self):
        """Export conversation to dict"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": self.get_messages()
        }
    
    def save(self, filepath: Path):
        """Save conversation to JSON file"""
        filepath.write_text(json.dumps(self.to_dict(), indent=2))


class MemoryManager:
    """Global memory manager for all sessions"""
    
    def __init__(self, persist_dir: Optional[Path] = None):
        self.sessions: Dict[str, ConversationMemory] = {}
        self.persist_dir = persist_dir or Path("chatbot/chat_history")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
    
    def get_or_create(self, session_id: str) -> ConversationMemory:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(session_id)
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def save_session(self, session_id: str):
        """Persist session to disk"""
        if session_id in self.sessions:
            filepath = self.persist_dir / f"{session_id}.json"
            self.sessions[session_id].save(filepath)
    
    def load_session(self, session_id: str) -> Optional[ConversationMemory]:
        """Load session from disk"""
        filepath = self.persist_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        
        try:
            data = json.loads(filepath.read_text())
            memory = ConversationMemory(session_id)
            memory.created_at = datetime.fromisoformat(data["created_at"])
            
            for msg_data in data["messages"]:
                msg = Message(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"])
                )
                memory.messages.append(msg)
            
            self.sessions[session_id] = memory
            return memory
        except Exception:
            return None
    
    def list_sessions(self) -> List[str]:
        """List all saved session IDs"""
        return [f.stem for f in self.persist_dir.glob("*.json")]


# Global memory manager instance
_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager"""
    return _memory_manager
