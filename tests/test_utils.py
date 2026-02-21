from langgraph_debug.utils import debug_node
from langgraph_debug.tracer import GraphTracer
from langgraph_debug.metrics import MetricsCollector
from langgraph_debug.debugger import GraphDebugger, DebugConfig

def test_debug_node_decorator():
    tracer = GraphTracer()
    metrics = MetricsCollector()
    dbg = GraphDebugger(DebugConfig())

    @debug_node(debugger=dbg, metrics=metrics, tracer=tracer, node_name="n")
    def node(state):
        state = dict(state)
        state["ok"] = True
        return state

    result = node({})
    assert result["ok"] is True
    # Ensure tracer recorded steps
    tracer.start_trace("t2")
    tracer.record_step("n", "enter", {})
    tracer.record_step("n", "exit", {"ok": True})
    tracer.end_trace()
