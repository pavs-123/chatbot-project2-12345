#!/usr/bin/env python3
"""
Standalone script to run the LangGraph example with SystemMessage and HumanMessage.
This demonstrates the same functionality as the notebook but can be run directly.
"""
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """State for our LangGraph with messages"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: str


def initialize_node(state: GraphState) -> GraphState:
    """Initialize with a system message"""
    print("\n=== INITIALIZE NODE ===")
    system_msg = SystemMessage(
        content="You are a helpful assistant that processes user requests step by step."
    )
    state["messages"] = [system_msg] + list(state.get("messages", []))
    state["next_step"] = "process"
    print(f"Added SystemMessage: {system_msg.content}")
    return state


def process_node(state: GraphState) -> GraphState:
    """Process the user's message"""
    print("\n=== PROCESS NODE ===")
    messages = state.get("messages", [])
    
    # Find the last human message
    human_msg = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            human_msg = msg
            break
    
    if human_msg:
        print(f"Processing HumanMessage: {human_msg.content}")
        
        # Simulate processing and create a response
        response = AIMessage(
            content=f"I received your message: '{human_msg.content}'. Processing it now..."
        )
        state["messages"].append(response)
        state["next_step"] = "finalize"
        print(f"Added AIMessage: {response.content}")
    else:
        print("No HumanMessage found!")
        state["next_step"] = "finalize"
    
    return state


def finalize_node(state: GraphState) -> GraphState:
    """Finalize the conversation"""
    print("\n=== FINALIZE NODE ===")
    final_msg = AIMessage(
        content="Task completed successfully!"
    )
    state["messages"].append(final_msg)
    print(f"Added final AIMessage: {final_msg.content}")
    return state


def router(state: GraphState) -> str:
    """Route to the next node based on next_step"""
    next_step = state.get("next_step", "END")
    print(f"\n>>> Routing to: {next_step}")
    return next_step


def build_message_graph():
    """Build a LangGraph with SystemMessage and HumanMessage routing"""
    
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("process", process_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add conditional edges (connecting nodes)
    workflow.add_conditional_edges(
        "initialize",
        router,
        {
            "process": "process",
            "finalize": "finalize",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "process",
        router,
        {
            "finalize": "finalize",
            "END": END
        }
    )
    
    # Add edge from finalize to END
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    return workflow.compile()


def print_messages(messages, title="MESSAGE HISTORY"):
    """Print all messages in a formatted way"""
    print(f"\n📝 {title}:")
    print("=" * 60)
    for i, msg in enumerate(messages, 1):
        msg_type = type(msg).__name__
        print(f"\n{i}. [{msg_type}]")
        print(f"   Content: {msg.content}")
    print("\n" + "=" * 60)


def main():
    """Run examples"""
    print("=" * 60)
    print("LANGGRAPH WITH SYSTEMMESSAGE AND HUMANMESSAGE")
    print("=" * 60)
    
    # Build the graph
    graph = build_message_graph()
    print("\n✅ Graph built successfully!\n")
    
    # Example 1: Single HumanMessage
    print("\n" + "=" * 60)
    print("EXAMPLE 1: SINGLE HUMAN MESSAGE")
    print("=" * 60)
    
    initial_state = {
        "messages": [
            HumanMessage(content="Hello! Can you help me understand LangGraph?")
        ],
        "next_step": "initialize"
    }
    
    result = graph.invoke(initial_state)
    print_messages(result["messages"], "FINAL MESSAGE HISTORY")
    
    # Example 2: Multiple HumanMessages
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: MULTIPLE HUMAN MESSAGES")
    print("=" * 60)
    
    conversation_state = {
        "messages": [
            HumanMessage(content="What is the weather like?"),
            HumanMessage(content="Can you also tell me about RAG?")
        ],
        "next_step": "initialize"
    }
    
    result2 = graph.invoke(conversation_state)
    print_messages(result2["messages"], "CONVERSATION HISTORY")
    
    # Graph structure
    print("\n\n📊 GRAPH STRUCTURE:")
    print("=" * 60)
    print("""
    START
      |
      v
  [initialize]  <-- Adds SystemMessage
      |
      | (router checks next_step)
      v
   [process]    <-- Processes HumanMessage, adds AIMessage
      |
      | (router checks next_step)
      v
   [finalize]   <-- Adds completion AIMessage
      |
      v
     END
    """)
    print("=" * 60)
    
    print("\n✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!\n")
    print("💡 Check the notebook for interactive visualization and more details.")
    print("📖 See graph_visualization.md for the Mermaid diagram.\n")


if __name__ == "__main__":
    main()
