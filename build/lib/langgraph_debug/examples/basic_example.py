"""
Basic LangGraph Example with Debugging and Metrics

This example demonstrates how to use the debugging and metrics tools
with a simple LangGraph application.
"""

import sys
import os
from typing import TypedDict, Annotated
import operator

# Add parent directory to path
# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langgraph.graph import StateGraph, END
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    _EXAMPLE_DEPS_OK = True
except Exception as _e:
    _EXAMPLE_DEPS_OK = False
    _EXAMPLE_DEPS_ERR = _e

# Import debugging tools
from langgraph_debug.debugger import GraphDebugger, DebugConfig, DebugLevel
from langgraph_debug.metrics import MetricsCollector
from langgraph_debug.tracer import GraphTracer
from langgraph_debug.visualizer import GraphVisualizer


# Define the state
class AgentState(TypedDict):
    """State for the agent"""
    messages: Annotated[list, operator.add]
    current_step: str
    result: str


# Create debugging and metrics instances
debug_config = DebugConfig(
    level=DebugLevel.DEBUG,
    log_inputs=True,
    log_outputs=True,
    log_state=True,
    log_timing=True,
    console_output=True,
)

debugger = GraphDebugger(debug_config)
metrics = MetricsCollector(cost_per_1k_input=0.0015, cost_per_1k_output=0.002)
tracer = GraphTracer()


def create_graph():
    """Create a simple LangGraph with debugging"""
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Define node functions with debugging
    def input_node(state: AgentState) -> AgentState:
        """Process input"""
        node_name = "input_node"
        
        # Start debugging and metrics
        debugger.log_node_entry(node_name, state)
        metrics.start_node(node_name)
        tracer.record_step(node_name, "enter", state)
        
        try:
            # Process
            state["current_step"] = "input_processed"
            state["messages"].append("User input received")
            
            # Log outputs
            debugger.log_node_exit(node_name, state, outputs=state["messages"])
            metrics.end_node(success=True, input_tokens=10, output_tokens=5)
            tracer.record_step(node_name, "exit", state)
            
        except Exception as e:
            debugger.log_error(node_name, e, state)
            metrics.end_node(success=False, error=str(e))
            raise
        
        return state
    
    def processing_node(state: AgentState) -> AgentState:
        """Main processing node"""
        node_name = "processing_node"
        
        debugger.log_node_entry(node_name, state)
        metrics.start_node(node_name)
        tracer.record_step(node_name, "enter", state)
        
        try:
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("user", "{input}")
            ])
            
            # Process with LLM
            chain = prompt | llm
            response = chain.invoke({"input": "Tell me a short joke about programming"})
            
            state["current_step"] = "processing_complete"
            state["messages"].append(f"AI Response: {response.content}")
            state["result"] = response.content
            
            debugger.log_node_exit(node_name, state, outputs=response.content)
            metrics.end_node(success=True, input_tokens=50, output_tokens=30)
            tracer.record_step(node_name, "exit", state)
            
        except Exception as e:
            debugger.log_error(node_name, e, state)
            metrics.end_node(success=False, error=str(e))
            raise
        
        return state
    
    def output_node(state: AgentState) -> AgentState:
        """Format output"""
        node_name = "output_node"
        
        debugger.log_node_entry(node_name, state)
        metrics.start_node(node_name)
        tracer.record_step(node_name, "enter", state)
        
        try:
            state["current_step"] = "output_formatted"
            state["messages"].append("Output ready")
            
            debugger.log_node_exit(node_name, state)
            metrics.end_node(success=True, input_tokens=5, output_tokens=3)
            tracer.record_step(node_name, "exit", state)
            
        except Exception as e:
            debugger.log_error(node_name, e, state)
            metrics.end_node(success=False, error=str(e))
            raise
        
        return state
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("processing", processing_node)
    workflow.add_node("output", output_node)
    
    # Add edges
    workflow.set_entry_point("input")
    workflow.add_edge("input", "processing")
    workflow.add_edge("processing", "output")
    workflow.add_edge("output", END)
    
    return workflow.compile()


def main():
    if not _EXAMPLE_DEPS_OK:
        print("[basic_example] Skipping: missing dependencies:", _EXAMPLE_DEPS_ERR)
        return
    """Run the example"""
    print("=" * 60)
    print("LangGraph Debugging and Metrics Example")
    print("=" * 60)
    
    # Start overall tracking
    metrics.start_graph("example_graph_1")
    tracer.start_trace("example_trace_1")
    
    # Create and run graph
    graph = create_graph()
    
    # Initial state
    initial_state = {
        "messages": [],
        "current_step": "start",
        "result": ""
    }
    
    print("\n🚀 Running graph...")
    
    try:
        # Execute graph
        final_state = graph.invoke(initial_state)
        
        print("\n✅ Execution completed!")
        print(f"\nFinal Result: {final_state.get('result', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
    
    # End tracking
    metrics.end_graph()
    tracer.end_trace()
    
    # Display debugging summary
    print("\n" + "=" * 60)
    print(debugger.get_summary())
    
    # Display metrics
    print("\n" + "=" * 60)
    summary = metrics.get_summary()
    print(GraphVisualizer.visualize_metrics_table(summary))
    
    # Display execution flow
    print("\n" + "=" * 60)
    events = debugger.get_events()
    print(GraphVisualizer.visualize_execution_flow(events))
    
    # Display execution path
    print("\n" + "=" * 60)
    execution_path = tracer.get_execution_path("example_trace_1")
    print(f"\nExecution Path: {' → '.join(execution_path)}")
    
    # Export reports
    print("\n" + "=" * 60)
    print("\n📄 Exporting reports...")
    
    # Export metrics
    metrics.export_metrics("debug_metrics.json")
    print("✓ Metrics exported to: debug_metrics.json")
    
    # Export events
    debugger.export_events("debug_events.json")
    print("✓ Events exported to: debug_events.json")
    
    # Export trace
    tracer.export_trace("example_trace_1", "debug_trace.json")
    print("✓ Trace exported to: debug_trace.json")
    
    # Create HTML report
    html_report = GraphVisualizer.create_html_report(summary, events, execution_path)
    with open("debug_report.html", "w") as f:
        f.write(html_report)
    print("✓ HTML report exported to: debug_report.html")
    
    print("\n" + "=" * 60)
    print("✨ Example completed! Check the exported files for detailed reports.")


if __name__ == "__main__":
    main()
