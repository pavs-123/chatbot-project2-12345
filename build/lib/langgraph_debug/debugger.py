"""
LangGraph Debugger - Advanced debugging utilities for LangGraph applications
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback


class DebugLevel(Enum):
    """Debug level enumeration"""
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


@dataclass
class DebugConfig:
    """Configuration for debugging"""
    level: DebugLevel = DebugLevel.INFO
    log_inputs: bool = True
    log_outputs: bool = True
    log_state: bool = True
    log_errors: bool = True
    log_timing: bool = True
    log_file: Optional[str] = None
    console_output: bool = True
    max_message_length: int = 1000
    truncate_long_messages: bool = True
    pretty_print: bool = True
    callbacks: List[Callable] = field(default_factory=list)


class GraphDebugger:
    """
    Advanced debugger for LangGraph applications.
    
    Features:
    - State tracking at each node
    - Input/output logging
    - Error capturing and stack traces
    - Timing information
    - Custom callbacks for debugging events
    """
    
    def __init__(self, config: Optional[DebugConfig] = None):
        self.config = config or DebugConfig()
        self.events: List[Dict[str, Any]] = []
        self.node_execution_count: Dict[str, int] = {}
        self.errors: List[Dict[str, Any]] = []
        
        # Setup logging
        self.logger = logging.getLogger("LangGraphDebugger")
        self.logger.setLevel(self._get_log_level())
        
        # Configure handlers
        if self.config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)
        
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)
    
    def _get_log_level(self) -> int:
        """Convert DebugLevel to logging level"""
        level_map = {
            DebugLevel.NONE: logging.CRITICAL,
            DebugLevel.ERROR: logging.ERROR,
            DebugLevel.WARNING: logging.WARNING,
            DebugLevel.INFO: logging.INFO,
            DebugLevel.DEBUG: logging.DEBUG,
            DebugLevel.TRACE: logging.DEBUG,
        }
        return level_map.get(self.config.level, logging.INFO)
    
    def _get_formatter(self) -> logging.Formatter:
        """Get log formatter"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _truncate(self, text: str) -> str:
        """Truncate long messages if configured"""
        if self.config.truncate_long_messages and len(text) > self.config.max_message_length:
            return text[:self.config.max_message_length] + "... [truncated]"
        return text
    
    def _format_data(self, data: Any) -> str:
        """Format data for logging"""
        try:
            if self.config.pretty_print:
                return json.dumps(data, indent=2, default=str)
            return json.dumps(data, default=str)
        except Exception:
            return str(data)
    
    def log_node_entry(self, node_name: str, state: Dict[str, Any], inputs: Optional[Dict] = None):
        """Log entry into a graph node"""
        if self.config.level.value < DebugLevel.DEBUG.value:
            return
        
        # Update execution count
        self.node_execution_count[node_name] = self.node_execution_count.get(node_name, 0) + 1
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "node_entry",
            "node_name": node_name,
            "execution_count": self.node_execution_count[node_name],
        }
        
        if self.config.log_inputs and inputs:
            event["inputs"] = inputs
        
        if self.config.log_state:
            event["state"] = state
        
        self.events.append(event)
        
        log_msg = f"→ Entering node: {node_name} (execution #{self.node_execution_count[node_name]})"
        if self.config.log_inputs and inputs:
            log_msg += f"\n  Inputs: {self._truncate(self._format_data(inputs))}"
        if self.config.log_state:
            log_msg += f"\n  State: {self._truncate(self._format_data(state))}"
        
        self.logger.debug(log_msg)
        self._trigger_callbacks(event)
    
    def log_node_exit(self, node_name: str, state: Dict[str, Any], outputs: Optional[Any] = None):
        """Log exit from a graph node"""
        if self.config.level.value < DebugLevel.DEBUG.value:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "node_exit",
            "node_name": node_name,
        }
        
        if self.config.log_outputs and outputs:
            event["outputs"] = outputs
        
        if self.config.log_state:
            event["state"] = state
        
        self.events.append(event)
        
        log_msg = f"← Exiting node: {node_name}"
        if self.config.log_outputs and outputs:
            log_msg += f"\n  Outputs: {self._truncate(self._format_data(outputs))}"
        if self.config.log_state:
            log_msg += f"\n  State: {self._truncate(self._format_data(state))}"
        
        self.logger.debug(log_msg)
        self._trigger_callbacks(event)
    
    def log_error(self, node_name: str, error: Exception, state: Optional[Dict] = None):
        """Log an error that occurred in a node"""
        if self.config.level.value < DebugLevel.ERROR.value:
            return
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "error",
            "node_name": node_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }
        
        if state:
            error_info["state"] = state
        
        self.errors.append(error_info)
        self.events.append(error_info)
        
        log_msg = f"✗ Error in node: {node_name}\n  {type(error).__name__}: {str(error)}"
        if state:
            log_msg += f"\n  State: {self._truncate(self._format_data(state))}"
        log_msg += f"\n  Traceback:\n{error_info['traceback']}"
        
        self.logger.error(log_msg)
        self._trigger_callbacks(error_info)
    
    def log_state_change(self, node_name: str, old_state: Dict, new_state: Dict):
        """Log state changes"""
        if self.config.level.value < DebugLevel.TRACE.value:
            return
        
        # Find differences
        changes = {}
        all_keys = set(old_state.keys()) | set(new_state.keys())
        
        for key in all_keys:
            old_val = old_state.get(key, "<<not present>>")
            new_val = new_state.get(key, "<<not present>>")
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}
        
        if not changes:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "state_change",
            "node_name": node_name,
            "changes": changes,
        }
        
        self.events.append(event)
        
        log_msg = f"⟳ State changed in node: {node_name}"
        for key, vals in changes.items():
            log_msg += f"\n  {key}: {self._truncate(str(vals['old']))} → {self._truncate(str(vals['new']))}"
        
        self.logger.debug(log_msg)
        self._trigger_callbacks(event)
    
    def log_timing(self, node_name: str, duration_seconds: float):
        """Log timing information for a node"""
        if not self.config.log_timing:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "timing",
            "node_name": node_name,
            "duration_seconds": duration_seconds,
        }
        
        self.events.append(event)
        
        self.logger.info(f"⏱ Node '{node_name}' executed in {duration_seconds:.3f}s")
        self._trigger_callbacks(event)
    
    def _trigger_callbacks(self, event: Dict[str, Any]):
        """Trigger registered callbacks"""
        for callback in self.config.callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.warning(f"Callback error: {e}")
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all logged events, optionally filtered by type"""
        if event_type:
            return [e for e in self.events if e.get("event_type") == event_type]
        return self.events
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all logged errors"""
        return self.errors
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get statistics about node executions"""
        timings = [e for e in self.events if e.get("event_type") == "timing"]
        timing_by_node = {}
        
        for timing in timings:
            node = timing["node_name"]
            if node not in timing_by_node:
                timing_by_node[node] = []
            timing_by_node[node].append(timing["duration_seconds"])
        
        stats = {}
        for node, durations in timing_by_node.items():
            stats[node] = {
                "count": len(durations),
                "total_time": sum(durations),
                "avg_time": sum(durations) / len(durations),
                "min_time": min(durations),
                "max_time": max(durations),
            }
        
        return stats
    
    def export_events(self, filepath: str):
        """Export all events to a JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.events, f, indent=2, default=str)
        self.logger.info(f"Events exported to {filepath}")
    
    def clear(self):
        """Clear all logged events and stats"""
        self.events.clear()
        self.errors.clear()
        self.node_execution_count.clear()
        self.logger.info("Debug data cleared")
    
    def get_summary(self) -> str:
        """Get a summary of the debugging session"""
        total_events = len(self.events)
        total_errors = len(self.errors)
        total_nodes = len(self.node_execution_count)
        
        summary = f"""
=== LangGraph Debug Summary ===
Total Events: {total_events}
Total Errors: {total_errors}
Unique Nodes: {total_nodes}

Node Execution Counts:
"""
        for node, count in sorted(self.node_execution_count.items()):
            summary += f"  {node}: {count}\n"
        
        if self.errors:
            summary += "\nErrors:\n"
            for error in self.errors:
                summary += f"  [{error['timestamp']}] {error['node_name']}: {error['error_type']}\n"
        
        stats = self.get_node_stats()
        if stats:
            summary += "\nTiming Statistics:\n"
            for node, node_stats in sorted(stats.items()):
                summary += f"  {node}:\n"
                summary += f"    Avg: {node_stats['avg_time']:.3f}s\n"
                summary += f"    Total: {node_stats['total_time']:.3f}s\n"
        
        return summary
