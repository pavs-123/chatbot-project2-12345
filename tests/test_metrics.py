import pytest
from langgraph_debug.metrics import MetricsCollector

def test_metrics_basic_flow():
    m = MetricsCollector(cost_per_1k_input=1.5, cost_per_1k_output=2.0)
    m.start_graph("g1")
    m.start_node("n1")
    m.end_node(success=True, input_tokens=100, output_tokens=200)
    m.end_graph()
    summary = m.get_summary()
    graphs = summary["graphs"]
    assert len(graphs) == 1
    g = graphs[0]
    assert g["total_nodes_executed"] == 1
    assert g["successful_nodes"] == 1
    assert g["failed_nodes"] == 0
    # cost: 0.1k*1.5 + 0.2k*2.0 = 0.15 + 0.4 = 0.55
    assert pytest.approx(summary["cost_estimate"]["total_cost"], 1e-6) == 0.55
