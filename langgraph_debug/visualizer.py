"""
LangGraph Visualizer - Visualization tools for graph execution and metrics
"""

from typing import Any, Dict, List, Optional
import json


class GraphVisualizer:
    """
    Visualization utilities for LangGraph debugging.
    
    Provides:
    - ASCII art graph visualization
    - Execution flow diagrams
    - Metrics tables
    - State change visualization
    """
    
    @staticmethod
    def visualize_execution_flow(steps: List[Dict[str, Any]]) -> str:
        """Create an ASCII visualization of execution flow"""
        if not steps:
            return "No execution steps recorded."
        
        output = ["\n=== Execution Flow ===\n"]
        
        for i, step in enumerate(steps, 1):
            node_name = step.get('node_name', 'unknown')
            event_type = step.get('event_type', 'unknown')
            timestamp = step.get('timestamp', '')
            
            # Format based on event type
            if event_type == 'node_entry' or event_type == 'enter':
                symbol = "→"
                action = "ENTER"
            elif event_type == 'node_exit' or event_type == 'exit':
                symbol = "←"
                action = "EXIT"
            elif event_type == 'error':
                symbol = "✗"
                action = "ERROR"
            elif event_type == 'state_change':
                symbol = "⟳"
                action = "STATE"
            else:
                symbol = "•"
                action = event_type.upper()
            
            output.append(f"{i:3d}. {symbol} [{action:6s}] {node_name}")
            
            # Add timing if available
            if 'duration_seconds' in step:
                output[-1] += f" ({step['duration_seconds']:.3f}s)"
            
            # Add error info if present
            if event_type == 'error' and 'error_message' in step:
                output.append(f"       └─ Error: {step['error_message']}")
        
        return "\n".join(output)
    
    @staticmethod
    def visualize_metrics_table(metrics: Dict[str, Any]) -> str:
        """Create a formatted table of metrics"""
        if not metrics:
            return "No metrics available."
        
        output = ["\n=== Metrics Summary ===\n"]
        
        # Node statistics
        if 'node_statistics' in metrics:
            output.append("Node Performance:")
            output.append("-" * 80)
            output.append(f"{'Node':<20} {'Count':>8} {'Avg Time':>12} {'Total Time':>12} {'Tokens':>10}")
            output.append("-" * 80)
            
            for node_name, stats in metrics['node_statistics'].items():
                if not stats:
                    continue
                
                count = stats.get('execution_count', 0)
                avg_time = stats.get('avg_duration', 0)
                total_time = stats.get('total_duration', 0)
                tokens = stats.get('total_tokens', 0)
                
                output.append(
                    f"{node_name:<20} {count:>8} {avg_time:>11.3f}s {total_time:>11.3f}s {tokens:>10}"
                )
            output.append("-" * 80)
        
        # Cost estimate
        if 'cost_estimate' in metrics:
            cost = metrics['cost_estimate']
            output.append("\nCost Estimate:")
            output.append(f"  Input Tokens:  {cost.get('input_tokens', 0):>10,}")
            output.append(f"  Output Tokens: {cost.get('output_tokens', 0):>10,}")
            output.append(f"  Total Tokens:  {cost.get('total_tokens', 0):>10,}")
            output.append(f"  Estimated Cost: ${cost.get('total_cost', 0):>8.4f}")
        
        # Overall stats
        if 'total_graphs_executed' in metrics:
            output.append("\nOverall Statistics:")
            output.append(f"  Graphs Executed: {metrics.get('total_graphs_executed', 0)}")
            output.append(f"  Total Time: {metrics.get('total_execution_time', 0):.3f}s")
            output.append(f"  Avg Time per Graph: {metrics.get('avg_graph_execution_time', 0):.3f}s")
        
        return "\n".join(output)
    
    @staticmethod
    def visualize_state_changes(changes: List[Dict[str, Any]]) -> str:
        """Visualize state changes over time"""
        if not changes:
            return "No state changes recorded."
        
        output = ["\n=== State Changes ===\n"]
        
        for change in changes:
            if change.get('event_type') != 'state_change':
                continue
            
            node_name = change.get('node_name', 'unknown')
            timestamp = change.get('timestamp', '')
            changes_dict = change.get('changes', {})
            
            output.append(f"Node: {node_name} @ {timestamp}")
            
            for key, vals in changes_dict.items():
                old_val = vals.get('old', '')
                new_val = vals.get('new', '')
                output.append(f"  {key}: {old_val} → {new_val}")
            
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def visualize_graph_structure(nodes: List[str], edges: List[tuple]) -> str:
        """Create ASCII visualization of graph structure"""
        output = ["\n=== Graph Structure ===\n"]
        
        # List nodes
        output.append("Nodes:")
        for node in nodes:
            output.append(f"  • {node}")
        
        # List edges
        output.append("\nEdges:")
        for source, target in edges:
            output.append(f"  {source} → {target}")
        
        return "\n".join(output)
    
    @staticmethod
    def create_mermaid_diagram(execution_path: List[str]) -> str:
        """Create a Mermaid diagram from execution path"""
        if not execution_path:
            return "graph TD\n  Start[No execution path]"
        
        lines = ["graph TD"]
        lines.append("  Start([Start])")
        
        # Create flow
        prev_node = "Start"
        for i, node in enumerate(execution_path):
            node_id = f"N{i}"
            lines.append(f"  {node_id}[{node}]")
            lines.append(f"  {prev_node} --> {node_id}")
            prev_node = node_id
        
        lines.append(f"  {prev_node} --> End([End])")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_html_report(
        metrics: Dict[str, Any],
        events: List[Dict[str, Any]],
        execution_path: List[str]
    ) -> str:
        """Create an HTML report with all visualizations"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>LangGraph Debug Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        tr:hover { background-color: #f5f5f5; }
        .metric-box {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            min-width: 150px;
        }
        .metric-label { font-size: 0.9em; opacity: 0.9; }
        .metric-value { font-size: 1.8em; font-weight: bold; }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .step { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 3px solid #007bff; }
        .error { border-left-color: #dc3545; background: #fff5f5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 LangGraph Debug Report</h1>
        <p>Generated: """ + f"{json.dumps(metrics.get('timestamp', 'N/A'))}" + """</p>
        
        <h2>📊 Overview</h2>
        <div>
            <div class="metric-box">
                <div class="metric-label">Total Graphs</div>
                <div class="metric-value">""" + str(metrics.get('total_graphs_executed', 0)) + """</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Total Events</div>
                <div class="metric-value">""" + str(len(events)) + """</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">$""" + f"{metrics.get('cost_estimate', {}).get('total_cost', 0):.4f}" + """</div>
            </div>
        </div>
        
        <h2>🎯 Execution Path</h2>
        <pre>""" + " → ".join(execution_path if execution_path else ["No path"]) + """</pre>
        
        <h2>📈 Node Performance</h2>
        <table>
            <tr>
                <th>Node</th>
                <th>Executions</th>
                <th>Avg Time (s)</th>
                <th>Total Time (s)</th>
                <th>Total Tokens</th>
            </tr>
"""
        
        # Add node statistics
        node_stats = metrics.get('node_statistics', {})
        for node_name, stats in node_stats.items():
            if stats:
                html += f"""
            <tr>
                <td>{node_name}</td>
                <td>{stats.get('execution_count', 0)}</td>
                <td>{stats.get('avg_duration', 0):.3f}</td>
                <td>{stats.get('total_duration', 0):.3f}</td>
                <td>{stats.get('total_tokens', 0)}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>📝 Execution Log</h2>
        <div>
"""
        
        # Add events
        for event in events[:50]:  # Limit to first 50 events
            event_type = event.get('event_type', 'unknown')
            node_name = event.get('node_name', 'N/A')
            error_class = ' error' if event_type == 'error' else ''
            
            html += f"""
            <div class="step{error_class}">
                <strong>{event_type.upper()}</strong>: {node_name}
                <small> @ {event.get('timestamp', 'N/A')}</small>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html
