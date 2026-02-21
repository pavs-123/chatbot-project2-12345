"""
Example using the @debug_node decorator for cleaner code

This shows how to use the decorator to automatically add debugging
without cluttering your node functions.
"""

import sys
import os
from typing import TypedDict

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langgraph.graph import StateGraph, END
from langgraph_debug.debugger import GraphDebugger, DebugConfig, DebugLevel
from langgraph_debug.metrics import MetricsCollector
from langgraph_debug.tracer import GraphTracer
from langgraph_debug.visualizer import GraphVisualizer
from langgraph_debug.utils import debug_node, DebugContext

# No external LLM dependencies required for this example


# Setup debugging tools
debugger = GraphDebugger(DebugConfig(level=DebugLevel.DEBUG))
metrics = MetricsCollector(cost_per_1k_input=0.0015, cost_per_1k_output=0.002)
tracer = GraphTracer()


class SimpleState(TypedDict):
    """Simple state for demonstration"""
    count: int
    message: str
    result: str


# Using the decorator - much cleaner!
@debug_node(debugger=debugger, metrics=metrics, tracer=tracer)
def increment_node(state: SimpleState) -> SimpleState:
    """Increment counter"""
    state["count"] += 1
    state["message"] = f"Count is now {state['count']}"
    return state


@debug_node(debugger=debugger, metrics=metrics, tracer=tracer)
def double_node(state: SimpleState) -> SimpleState:
    """Double the counter"""
    state["count"] *= 2
    state["message"] = f"Doubled to {state['count']}"
    return state


@debug_node(debugger=debugger, metrics=metrics, tracer=tracer)
def finalize_node(state: SimpleState) -> SimpleState:
    """Finalize result"""
    state["result"] = f"Final count: {state['count']}"
    return state


def create_simple_graph():
    """Create a simple graph with decorated nodes"""
    workflow = StateGraph(SimpleState)
    
    workflow.add_node("increment", increment_node)
    workflow.add_node("double", double_node)
    workflow.add_node("finalize", finalize_node)
    
    workflow.set_entry_point("increment")
    workflow.add_edge("increment", "double")
    workflow.add_edge("double", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


def main():
    """Run the decorator example"""
    print("=" * 60)
    print("LangGraph Debugging - Decorator Example")
    print("=" * 60)
    
    graph = create_simple_graph()
    
    # Using the context manager for cleaner code
    with DebugContext(debugger, metrics, tracer, "decorator_example"):
        initial_state = {
            "count": 5,
            "message": "",
            "result": ""
        }
        
        print("\n🚀 Running graph with initial count: 5")
        
        final_state = graph.invoke(initial_state)
        
        print(f"\n✅ {final_state['result']}")
    
    # Display results
    print("\n" + "=" * 60)
    print(debugger.get_summary())
    
    print("\n" + "=" * 60)
    summary = metrics.get_summary()
    print(GraphVisualizer.visualize_metrics_table(summary))
    
    print("\n" + "=" * 60)
    execution_path = tracer.get_execution_path("decorator_example")
    print(f"Execution Path: {' → '.join(execution_path)}")
    
    print("\n✨ Decorator example completed!")
    print("Notice how clean the node functions are - no debugging code!")


if __name__ == "__main__":
    main()
