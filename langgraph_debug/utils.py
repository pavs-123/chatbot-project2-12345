"""
Utility functions for LangGraph debugging and metrics
"""

import functools
import time
from typing import Callable, Any, Optional
from .debugger import GraphDebugger
from .metrics import MetricsCollector
from .tracer import GraphTracer


def debug_node(
    debugger: Optional[GraphDebugger] = None,
    metrics: Optional[MetricsCollector] = None,
    tracer: Optional[GraphTracer] = None,
    node_name: Optional[str] = None
):
    """
    Decorator to automatically add debugging to a node function.
    
    Usage:
        @debug_node(debugger=my_debugger, metrics=my_metrics)
        def my_node(state):
            # Your node logic
            return state
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(state: Any) -> Any:
            name = node_name or func.__name__
            start_time = time.time()
            
            # Log entry
            if debugger:
                debugger.log_node_entry(name, state)
            if metrics:
                metrics.start_node(name)
            if tracer:
                tracer.record_step(name, "enter", state)
            
            try:
                # Execute the actual function
                result = func(state)
                
                # Log exit
                duration = time.time() - start_time
                
                if debugger:
                    debugger.log_node_exit(name, result)
                    debugger.log_timing(name, duration)
                
                if metrics:
                    # Try to extract token info from result if available
                    tokens_in = getattr(result, 'input_tokens', 0)
                    tokens_out = getattr(result, 'output_tokens', 0)
                    metrics.end_node(success=True, input_tokens=tokens_in, output_tokens=tokens_out)
                
                if tracer:
                    tracer.record_step(name, "exit", result)
                
                return result
                
            except Exception as e:
                # Log error
                if debugger:
                    debugger.log_error(name, e, state)
                if metrics:
                    metrics.end_node(success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


class DebugContext:
    """
    Context manager for graph execution with automatic debugging.
    
    Usage:
        with DebugContext(debugger, metrics, tracer, "my_graph") as ctx:
            result = graph.invoke(state)
    """
    
    def __init__(
        self,
        debugger: Optional[GraphDebugger] = None,
        metrics: Optional[MetricsCollector] = None,
        tracer: Optional[GraphTracer] = None,
        graph_id: Optional[str] = None
    ):
        self.debugger = debugger
        self.metrics = metrics
        self.tracer = tracer
        self.graph_id = graph_id
    
    def __enter__(self):
        if self.metrics:
            self.metrics.start_graph(self.graph_id)
        if self.tracer:
            self.tracer.start_trace(self.graph_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.metrics:
            self.metrics.end_graph()
        if self.tracer:
            self.tracer.end_trace()
        
        if exc_type is not None and self.debugger:
            self.debugger.log_error("graph", exc_val, {})
        
        return False  # Don't suppress exceptions


def format_tokens(tokens: int) -> str:
    """Format token count for display"""
    if tokens >= 1_000_000:
        return f"{tokens/1_000_000:.2f}M"
    elif tokens >= 1_000:
        return f"{tokens/1_000:.2f}K"
    else:
        return str(tokens)


def format_duration(seconds: float) -> str:
    """Format duration for display"""
    if seconds >= 60:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    elif seconds >= 1:
        return f"{seconds:.2f}s"
    else:
        return f"{seconds*1000:.0f}ms"


def format_cost(cost: float) -> str:
    """Format cost for display"""
    if cost >= 1:
        return f"${cost:.2f}"
    elif cost >= 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.6f}"
