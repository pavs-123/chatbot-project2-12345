"""
Advanced LangGraph Example with Conditional Routing and State Management

This example demonstrates advanced debugging with:
- Conditional edges
- Multiple execution paths
- State transformations
- Error handling
"""

import sys
import os
from typing import TypedDict, Literal
import time

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langgraph.graph import StateGraph, END
from langgraph_debug.debugger import GraphDebugger, DebugConfig, DebugLevel
from langgraph_debug.metrics import MetricsCollector
from langgraph_debug.tracer import GraphTracer
from langgraph_debug.visualizer import GraphVisualizer

try:
    # Optional deps for advanced flows (if you later add LLMs)
    _ADV_DEPS_OK = True
except Exception as _e:
    _ADV_DEPS_OK = False
    _ADV_DEPS_ERR = _e


class AdvancedState(TypedDict):
    """Advanced state with routing logic"""
    input_text: str
    sentiment: str
    processing_type: str
    output: str
    error: str
    retry_count: int


# Setup debugging
debugger = GraphDebugger(DebugConfig(level=DebugLevel.TRACE, log_timing=True))
metrics = MetricsCollector(cost_per_1k_input=0.0015, cost_per_1k_output=0.002)
tracer = GraphTracer()


def analyze_sentiment(state: AdvancedState) -> AdvancedState:
    """Analyze sentiment of input"""
    node_name = "analyze_sentiment"
    debugger.log_node_entry(node_name, state)
    metrics.start_node(node_name)
    tracer.record_step(node_name, "enter", state)
    
    start_time = time.time()
    
    try:
        # Simple sentiment analysis (mock)
        text = state["input_text"].lower()
        
        if any(word in text for word in ["happy", "great", "awesome", "love"]):
            state["sentiment"] = "positive"
        elif any(word in text for word in ["sad", "bad", "terrible", "hate"]):
            state["sentiment"] = "negative"
        else:
            state["sentiment"] = "neutral"
        
        duration = time.time() - start_time
        
        debugger.log_node_exit(node_name, state, outputs=state["sentiment"])
        debugger.log_timing(node_name, duration)
        metrics.end_node(success=True, input_tokens=20, output_tokens=5)
        tracer.record_step(node_name, "exit", state)
        
    except Exception as e:
        debugger.log_error(node_name, e, state)
        metrics.end_node(success=False, error=str(e))
        state["error"] = str(e)
        raise
    
    return state


def process_positive(state: AdvancedState) -> AdvancedState:
    """Process positive sentiment"""
    node_name = "process_positive"
    debugger.log_node_entry(node_name, state)
    metrics.start_node(node_name)
    tracer.record_step(node_name, "enter", state)
    
    try:
        state["processing_type"] = "positive_processing"
        state["output"] = f"Positive vibes detected! 😊 Original: {state['input_text']}"
        
        debugger.log_node_exit(node_name, state)
        metrics.end_node(success=True, input_tokens=15, output_tokens=10)
        tracer.record_step(node_name, "exit", state)
        
    except Exception as e:
        debugger.log_error(node_name, e, state)
        metrics.end_node(success=False, error=str(e))
        raise
    
    return state


def process_negative(state: AdvancedState) -> AdvancedState:
    """Process negative sentiment"""
    node_name = "process_negative"
    debugger.log_node_entry(node_name, state)
    metrics.start_node(node_name)
    tracer.record_step(node_name, "enter", state)
    
    try:
        state["processing_type"] = "negative_processing"
        state["output"] = f"Let's turn that frown upside down! 🙃 Original: {state['input_text']}"
        
        debugger.log_node_exit(node_name, state)
        metrics.end_node(success=True, input_tokens=15, output_tokens=12)
        tracer.record_step(node_name, "exit", state)
        
    except Exception as e:
        debugger.log_error(node_name, e, state)
        metrics.end_node(success=False, error=str(e))
        raise
    
    return state


def process_neutral(state: AdvancedState) -> AdvancedState:
    """Process neutral sentiment"""
    node_name = "process_neutral"
    debugger.log_node_entry(node_name, state)
    metrics.start_node(node_name)
    tracer.record_step(node_name, "enter", state)
    
    try:
        state["processing_type"] = "neutral_processing"
        state["output"] = f"Balanced perspective! 😐 Original: {state['input_text']}"
        
        debugger.log_node_exit(node_name, state)
        metrics.end_node(success=True, input_tokens=15, output_tokens=8)
        tracer.record_step(node_name, "exit", state)
        
    except Exception as e:
        debugger.log_error(node_name, e, state)
        metrics.end_node(success=False, error=str(e))
        raise
    
    return state


def route_by_sentiment(state: AdvancedState) -> Literal["positive", "negative", "neutral"]:
    """Route based on sentiment analysis"""
    sentiment = state.get("sentiment", "neutral")
    debugger.logger.info(f"🔀 Routing to: {sentiment}")
    return sentiment


def create_advanced_graph():
    """Create graph with conditional routing"""
    workflow = StateGraph(AdvancedState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_sentiment)
    workflow.add_node("positive", process_positive)
    workflow.add_node("negative", process_negative)
    workflow.add_node("neutral", process_neutral)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        route_by_sentiment,
        {
            "positive": "positive",
            "negative": "negative",
            "neutral": "neutral",
        }
    )
    
    # All processing nodes lead to END
    workflow.add_edge("positive", END)
    workflow.add_edge("negative", END)
    workflow.add_edge("neutral", END)
    
    return workflow.compile()


def main():
    if not _ADV_DEPS_OK:
        print("[advanced_example] Skipping: missing optional dependencies:", _ADV_DEPS_ERR)
        return
    """Run advanced example"""
    print("=" * 70)
    print("Advanced LangGraph Debugging - Conditional Routing Example")
    print("=" * 70)
    
    # Test cases with different sentiments
    test_cases = [
        "I love this awesome product!",
        "This is terrible and I hate it.",
        "The weather is okay today.",
    ]
    
    graph = create_advanced_graph()
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test_input}")
        print('='*70)
        
        # Start tracking
        graph_id = f"advanced_graph_{i}"
        trace_id = f"advanced_trace_{i}"
        
        metrics.start_graph(graph_id, metadata={"test_case": i, "input": test_input})
        tracer.start_trace(trace_id)
        
        # Initial state
        initial_state = {
            "input_text": test_input,
            "sentiment": "",
            "processing_type": "",
            "output": "",
            "error": "",
            "retry_count": 0,
        }
        
        try:
            # Execute
            final_state = graph.invoke(initial_state)
            
            print(f"\n✅ Sentiment: {final_state['sentiment']}")
            print(f"📝 Output: {final_state['output']}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        # End tracking
        metrics.end_graph()
        tracer.end_trace()
        
        # Show execution path
        execution_path = tracer.get_execution_path(trace_id)
        print(f"🛤️  Path: {' → '.join(execution_path)}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    print(debugger.get_summary())
    
    summary = metrics.get_summary()
    print(GraphVisualizer.visualize_metrics_table(summary))
    
    # Node statistics
    print("\n" + "=" * 70)
    print("Node Statistics:")
    node_stats = metrics.get_node_stats()
    for node_name, stats in node_stats.items():
        if stats:
            print(f"\n{node_name}:")
            print(f"  Executions: {stats['execution_count']}")
            print(f"  Avg Time: {stats['avg_duration']:.3f}s")
            print(f"  Total Tokens: {stats['total_tokens']}")
    
    # Export all data
    print("\n" + "=" * 70)
    print("📄 Exporting reports...")
    
    metrics.export_metrics("advanced_metrics.json")
    debugger.export_events("advanced_events.json")
    tracer.export_all_traces("advanced_traces.json")
    
    # Create Mermaid diagram for last execution
    last_path = tracer.get_execution_path(f"advanced_trace_{len(test_cases)}")
    mermaid = GraphVisualizer.create_mermaid_diagram(last_path)
    
    print("\n📊 Mermaid Diagram (copy to mermaid.live):")
    print(mermaid)
    
    print("\n✨ Advanced example completed!")


if __name__ == "__main__":
    main()
