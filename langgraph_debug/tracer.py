"""
LangGraph Tracer - Execution tracing and flow visualization
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ExecutionStep:
    """Single step in the execution trace"""
    step_id: int
    timestamp: str
    node_name: str
    event_type: str  # 'enter', 'exit', 'error'
    state_snapshot: Dict[str, Any]
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Complete execution trace for a graph"""
    trace_id: str
    start_time: str
    end_time: Optional[str] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    graph_structure: Optional[Dict] = None
    
    def add_step(self, step: ExecutionStep):
        """Add a step to the trace"""
        self.steps.append(step)
    
    def finalize(self):
        """Finalize the trace"""
        self.end_time = datetime.now().isoformat()


class GraphTracer:
    """
    Execution tracer for LangGraph applications.
    
    Captures the complete execution flow including:
    - Node transitions
    - State changes
    - Execution order
    - Timing information
    """
    
    def __init__(self):
        self.traces: List[ExecutionTrace] = []
        self.current_trace: Optional[ExecutionTrace] = None
        self.step_counter = 0
    
    def start_trace(self, trace_id: Optional[str] = None, graph_structure: Optional[Dict] = None):
        """Start a new execution trace"""
        if trace_id is None:
            trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.current_trace = ExecutionTrace(
            trace_id=trace_id,
            start_time=datetime.now().isoformat(),
            graph_structure=graph_structure
        )
        self.step_counter = 0
    
    def record_step(
        self,
        node_name: str,
        event_type: str,
        state: Dict[str, Any],
        metadata: Optional[Dict] = None
    ):
        """Record a step in the execution"""
        if self.current_trace is None:
            return
        
        self.step_counter += 1
        
        step = ExecutionStep(
            step_id=self.step_counter,
            timestamp=datetime.now().isoformat(),
            node_name=node_name,
            event_type=event_type,
            state_snapshot=state.copy() if state else {},
            metadata=metadata or {}
        )
        
        self.current_trace.add_step(step)
    
    def end_trace(self) -> Optional[ExecutionTrace]:
        """End the current trace"""
        if self.current_trace is None:
            return None
        
        self.current_trace.finalize()
        self.traces.append(self.current_trace)
        
        finished_trace = self.current_trace
        self.current_trace = None
        
        return finished_trace
    
    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Get a specific trace by ID"""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None
    
    def get_all_traces(self) -> List[ExecutionTrace]:
        """Get all traces"""
        return self.traces
    
    def export_trace(self, trace_id: str, filepath: str):
        """Export a specific trace to JSON"""
        trace = self.get_trace(trace_id)
        if trace:
            with open(filepath, 'w') as f:
                json.dump(self._trace_to_dict(trace), f, indent=2, default=str)
    
    def export_all_traces(self, filepath: str):
        """Export all traces to JSON"""
        traces_data = [self._trace_to_dict(t) for t in self.traces]
        with open(filepath, 'w') as f:
            json.dump(traces_data, f, indent=2, default=str)
    
    def _trace_to_dict(self, trace: ExecutionTrace) -> Dict:
        """Convert trace to dictionary"""
        return {
            "trace_id": trace.trace_id,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "graph_structure": trace.graph_structure,
            "steps": [
                {
                    "step_id": step.step_id,
                    "timestamp": step.timestamp,
                    "node_name": step.node_name,
                    "event_type": step.event_type,
                    "state_snapshot": step.state_snapshot,
                    "duration": step.duration,
                    "metadata": step.metadata,
                }
                for step in trace.steps
            ],
        }
    
    def get_execution_path(self, trace_id: str) -> List[str]:
        """Get the execution path (sequence of nodes) for a trace"""
        trace = self.get_trace(trace_id)
        if not trace:
            return []
        
        path = []
        for step in trace.steps:
            if step.event_type == 'enter':
                path.append(step.node_name)
        
        return path
    
    def clear(self):
        """Clear all traces"""
        self.traces.clear()
        self.current_trace = None
        self.step_counter = 0
