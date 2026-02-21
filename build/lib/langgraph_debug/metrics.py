"""
LangGraph Metrics - Comprehensive metrics collection for LangGraph applications
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import json


@dataclass
class NodeMetrics:
    """Metrics for a single node execution"""
    node_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark the node execution as complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error


@dataclass
class GraphMetrics:
    """Overall metrics for a graph execution"""
    graph_id: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    total_nodes_executed: int = 0
    successful_nodes: int = 0
    failed_nodes: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    node_metrics: List[NodeMetrics] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self):
        """Mark the graph execution as complete"""
        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time
        
        # Aggregate metrics
        for node_metric in self.node_metrics:
            self.total_nodes_executed += 1
            if node_metric.success:
                self.successful_nodes += 1
            else:
                self.failed_nodes += 1
            
            self.total_input_tokens += node_metric.input_tokens
            self.total_output_tokens += node_metric.output_tokens
            self.total_tokens += node_metric.total_tokens


class MetricsCollector:
    """
    Comprehensive metrics collector for LangGraph applications.
    
    Features:
    - Node execution tracking
    - Token usage monitoring
    - Performance metrics
    - Cost estimation
    - Aggregated statistics
    """
    
    def __init__(self, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        """
        Initialize metrics collector.
        
        Args:
            cost_per_1k_input: Cost per 1000 input tokens (for cost estimation)
            cost_per_1k_output: Cost per 1000 output tokens (for cost estimation)
        """
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        
        self.graph_metrics: List[GraphMetrics] = []
        self.current_graph: Optional[GraphMetrics] = None
        self.current_node: Optional[NodeMetrics] = None
        
        # Aggregated statistics
        self.total_graphs_executed = 0
        self.total_execution_time = 0.0
        self.node_execution_counts: Dict[str, int] = defaultdict(int)
        self.node_durations: Dict[str, List[float]] = defaultdict(list)
        self.node_token_usage: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"input": 0, "output": 0, "total": 0}
        )
    
    def start_graph(self, graph_id: Optional[str] = None, metadata: Optional[Dict] = None) -> GraphMetrics:
        """Start tracking a new graph execution"""
        if graph_id is None:
            graph_id = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.current_graph = GraphMetrics(
            graph_id=graph_id,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        return self.current_graph
    
    def end_graph(self) -> Optional[GraphMetrics]:
        """End tracking the current graph execution"""
        if self.current_graph is None:
            return None
        
        self.current_graph.complete()
        self.graph_metrics.append(self.current_graph)
        
        # Update aggregated stats
        self.total_graphs_executed += 1
        if self.current_graph.total_duration:
            self.total_execution_time += self.current_graph.total_duration
        
        finished_graph = self.current_graph
        self.current_graph = None
        
        return finished_graph
    
    def start_node(self, node_name: str, metadata: Optional[Dict] = None) -> NodeMetrics:
        """Start tracking a node execution"""
        self.current_node = NodeMetrics(
            node_name=node_name,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        self.node_execution_counts[node_name] += 1
        
        return self.current_node
    
    def end_node(
        self,
        success: bool = True,
        error: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> Optional[NodeMetrics]:
        """End tracking the current node execution"""
        if self.current_node is None:
            return None
        
        self.current_node.complete(success=success, error=error)
        self.current_node.input_tokens = input_tokens
        self.current_node.output_tokens = output_tokens
        self.current_node.total_tokens = input_tokens + output_tokens
        
        # Update aggregated stats
        node_name = self.current_node.node_name
        if self.current_node.duration:
            self.node_durations[node_name].append(self.current_node.duration)
        
        self.node_token_usage[node_name]["input"] += input_tokens
        self.node_token_usage[node_name]["output"] += output_tokens
        self.node_token_usage[node_name]["total"] += input_tokens + output_tokens
        
        # Add to current graph if exists
        if self.current_graph:
            self.current_graph.node_metrics.append(self.current_node)
        
        finished_node = self.current_node
        self.current_node = None
        
        return finished_node
    
    def get_node_stats(self, node_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific node or all nodes"""
        if node_name:
            durations = self.node_durations.get(node_name, [])
            tokens = self.node_token_usage.get(node_name, {"input": 0, "output": 0, "total": 0})
            
            if not durations:
                return {}
            
            return {
                "node_name": node_name,
                "execution_count": self.node_execution_counts.get(node_name, 0),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_duration": sum(durations),
                "total_input_tokens": tokens["input"],
                "total_output_tokens": tokens["output"],
                "total_tokens": tokens["total"],
                "avg_tokens_per_execution": tokens["total"] / len(durations) if durations else 0,
            }
        else:
            # Return stats for all nodes
            stats = {}
            for node in self.node_execution_counts.keys():
                stats[node] = self.get_node_stats(node)
            return stats
    
    def get_cost_estimate(self) -> Dict[str, float]:
        """Estimate costs based on token usage"""
        total_input_tokens = sum(usage["input"] for usage in self.node_token_usage.values())
        total_output_tokens = sum(usage["output"] for usage in self.node_token_usage.values())
        
        input_cost = (total_input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (total_output_tokens / 1000) * self.cost_per_1k_output
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all metrics"""
        return {
            "total_graphs_executed": self.total_graphs_executed,
            "total_execution_time": self.total_execution_time,
            "avg_graph_execution_time": (
                self.total_execution_time / self.total_graphs_executed
                if self.total_graphs_executed > 0 else 0
            ),
            "node_statistics": self.get_node_stats(),
            "cost_estimate": self.get_cost_estimate(),
            "graphs": [asdict(g) for g in self.graph_metrics],
        }
    
    def export_metrics(self, filepath: str):
        """Export all metrics to a JSON file"""
        summary = self.get_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def clear(self):
        """Clear all collected metrics"""
        self.graph_metrics.clear()
        self.current_graph = None
        self.current_node = None
        self.total_graphs_executed = 0
        self.total_execution_time = 0.0
        self.node_execution_counts.clear()
        self.node_durations.clear()
        self.node_token_usage.clear()
