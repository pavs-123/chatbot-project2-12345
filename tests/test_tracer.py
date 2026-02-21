from langgraph_debug.tracer import GraphTracer

def test_tracer_path():
    t = GraphTracer()
    t.start_trace("t1", graph_structure={"nodes": ["a", "b"]})
    t.record_step("a", "enter", {"x": 1})
    t.record_step("a", "exit", {"x": 2})
    t.record_step("b", "enter", {"y": 3})
    t.record_step("b", "exit", {"y": 4})
    trace = t.end_trace()
    assert trace is not None
    path = t.get_execution_path("t1")
    assert path == ["a", "b"]
