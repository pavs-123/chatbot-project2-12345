# 🔍 LangGraph Debugging and Metrics

A comprehensive debugging and metrics collection toolkit for LangGraph applications. This module provides everything you need to monitor, debug, and optimize your LangGraph workflows.

## 🎯 Features

### 1. **Advanced Debugging** (`debugger.py`)
- 📝 Detailed event logging (node entry/exit, state changes, errors)
- ⏱️ Timing information for performance analysis
- 🎚️ Configurable debug levels (NONE, ERROR, WARNING, INFO, DEBUG, TRACE)
- 📊 Export debug data to JSON
- 🔔 Custom callback support for real-time monitoring
- 📄 Console and file logging

### 2. **Comprehensive Metrics** (`metrics.py`)
- 📈 Node execution tracking and statistics
- 🪙 Token usage monitoring (input/output/total)
- 💰 Cost estimation based on token usage
- ⚡ Performance metrics (duration, throughput)
- 📊 Aggregated statistics across multiple runs
- 💾 Export metrics to JSON

### 3. **Execution Tracing** (`tracer.py`)
- 🗺️ Complete execution flow capture
- 📸 State snapshots at each step
- 🔄 Execution path visualization
- 💾 Trace export to JSON
- 🔍 Historical trace analysis

### 4. **Visualization Tools** (`visualizer.py`)
- 🎨 ASCII art execution flow diagrams
- 📊 Formatted metrics tables
- 🔄 State change visualization
- 🌐 HTML report generation
- 📐 Mermaid diagram generation

## 📦 Installation

This module is designed to work with your existing LangGraph project. Make sure you have the required dependencies:

```bash
# Using pip
pip install langgraph langchain langchain-openai

# Using uv (recommended)
uv pip install langgraph langchain langchain-openai
```

## 🚀 Quick Start

### Basic Usage

```python
from langgraph.graph import StateGraph, END
from debugger import GraphDebugger, DebugConfig, DebugLevel
from metrics import MetricsCollector
from tracer import GraphTracer

# Initialize debugging tools
debugger = GraphDebugger(DebugConfig(level=DebugLevel.DEBUG))
metrics = MetricsCollector(cost_per_1k_input=0.0015, cost_per_1k_output=0.002)
tracer = GraphTracer()

# Start tracking
metrics.start_graph("my_graph")
tracer.start_trace("my_trace")

# In your node functions
def my_node(state):
    node_name = "my_node"
    
    # Log entry
    debugger.log_node_entry(node_name, state)
    metrics.start_node(node_name)
    tracer.record_step(node_name, "enter", state)
    
    try:
        # Your processing logic here
        result = process_data(state)
        
        # Log exit
        debugger.log_node_exit(node_name, state, outputs=result)
        metrics.end_node(success=True, input_tokens=50, output_tokens=30)
        tracer.record_step(node_name, "exit", state)
        
        return result
        
    except Exception as e:
        debugger.log_error(node_name, e, state)
        metrics.end_node(success=False, error=str(e))
        raise

# After execution
metrics.end_graph()
tracer.end_trace()

# View results
print(debugger.get_summary())
print(metrics.get_summary())
```

## 📚 Examples

### Basic Example
See `examples/basic_example.py` for a complete working example with:
- Simple sequential graph
- Full debugging integration
- Metrics collection
- Report generation

Run it:
```bash
cd examples
python basic_example.py
```

### Advanced Example
See `examples/advanced_example.py` for advanced features:
- Conditional routing
- Multiple execution paths
- Sentiment analysis
- Comparative metrics

Run it:
```bash
cd examples
python advanced_example.py
```

## 🔧 Configuration

### Debug Configuration

```python
from debugger import DebugConfig, DebugLevel

config = DebugConfig(
    level=DebugLevel.DEBUG,           # Debug level
    log_inputs=True,                   # Log node inputs
    log_outputs=True,                  # Log node outputs
    log_state=True,                    # Log state changes
    log_errors=True,                   # Log errors
    log_timing=True,                   # Log timing info
    log_file="debug.log",              # Optional log file
    console_output=True,               # Console output
    max_message_length=1000,           # Max message length
    truncate_long_messages=True,       # Truncate long messages
    pretty_print=True,                 # Pretty print JSON
    callbacks=[my_callback_function]   # Custom callbacks
)
```

### Metrics Configuration

```python
from metrics import MetricsCollector

# Initialize with cost information (optional)
metrics = MetricsCollector(
    cost_per_1k_input=0.0015,   # Cost per 1000 input tokens
    cost_per_1k_output=0.002     # Cost per 1000 output tokens
)
```

## 📊 Available Debug Levels

- `NONE` (0): No logging
- `ERROR` (1): Only errors
- `WARNING` (2): Errors and warnings
- `INFO` (3): General information
- `DEBUG` (4): Detailed debugging
- `TRACE` (5): Maximum verbosity with state changes

## 🛠️ API Reference

### GraphDebugger

```python
# Core methods
debugger.log_node_entry(node_name, state, inputs=None)
debugger.log_node_exit(node_name, state, outputs=None)
debugger.log_error(node_name, error, state=None)
debugger.log_state_change(node_name, old_state, new_state)
debugger.log_timing(node_name, duration_seconds)

# Query methods
debugger.get_events(event_type=None)
debugger.get_errors()
debugger.get_node_stats()
debugger.get_summary()

# Export methods
debugger.export_events(filepath)
debugger.clear()
```

### MetricsCollector

```python
# Tracking methods
metrics.start_graph(graph_id=None, metadata=None)
metrics.end_graph()
metrics.start_node(node_name, metadata=None)
metrics.end_node(success=True, error=None, input_tokens=0, output_tokens=0)

# Query methods
metrics.get_node_stats(node_name=None)
metrics.get_cost_estimate()
metrics.get_summary()

# Export methods
metrics.export_metrics(filepath)
metrics.clear()
```

### GraphTracer

```python
# Tracking methods
tracer.start_trace(trace_id=None, graph_structure=None)
tracer.record_step(node_name, event_type, state, metadata=None)
tracer.end_trace()

# Query methods
tracer.get_trace(trace_id)
tracer.get_all_traces()
tracer.get_execution_path(trace_id)

# Export methods
tracer.export_trace(trace_id, filepath)
tracer.export_all_traces(filepath)
tracer.clear()
```

### GraphVisualizer

```python
# Static methods for visualization
GraphVisualizer.visualize_execution_flow(steps)
GraphVisualizer.visualize_metrics_table(metrics)
GraphVisualizer.visualize_state_changes(changes)
GraphVisualizer.visualize_graph_structure(nodes, edges)
GraphVisualizer.create_mermaid_diagram(execution_path)
GraphVisualizer.create_html_report(metrics, events, execution_path)
```

## 📈 Output Examples

### Execution Flow
```
=== Execution Flow ===

  1. → [ENTER ] input_node
  2. ← [EXIT  ] input_node (0.023s)
  3. → [ENTER ] processing_node
  4. ← [EXIT  ] processing_node (1.234s)
  5. → [ENTER ] output_node
  6. ← [EXIT  ] output_node (0.015s)
```

### Metrics Table
```
=== Metrics Summary ===

Node Performance:
--------------------------------------------------------------------------------
Node                    Count     Avg Time   Total Time     Tokens
--------------------------------------------------------------------------------
input_node                  1        0.023s        0.023s         15
processing_node             1        1.234s        1.234s         80
output_node                 1        0.015s        0.015s          8
--------------------------------------------------------------------------------

Cost Estimate:
  Input Tokens:          65
  Output Tokens:         38
  Total Tokens:         103
  Estimated Cost:  $0.0002
```

## 🎨 Generated Reports

The toolkit generates several types of reports:

1. **JSON Metrics** (`debug_metrics.json`) - Raw metrics data
2. **JSON Events** (`debug_events.json`) - All debug events
3. **JSON Traces** (`debug_trace.json`) - Execution traces
4. **HTML Report** (`debug_report.html`) - Interactive HTML dashboard

## 🔍 Use Cases

### Development & Testing
- Debug complex graph flows
- Understand execution order
- Identify bottlenecks
- Validate state transitions

### Production Monitoring
- Track performance metrics
- Monitor token usage and costs
- Capture errors and exceptions
- Analyze execution patterns

### Optimization
- Identify slow nodes
- Optimize token usage
- Reduce execution time
- Minimize costs

## 💡 Best Practices

1. **Use appropriate debug levels**
   - Development: `DEBUG` or `TRACE`
   - Production: `WARNING` or `ERROR`

2. **Export data regularly**
   - Save metrics for historical analysis
   - Keep debug logs for troubleshooting

3. **Monitor costs**
   - Set up cost tracking from the start
   - Review token usage regularly

4. **Use callbacks for real-time monitoring**
   - Integrate with monitoring systems
   - Send alerts on errors

5. **Clean up after testing**
   - Use `clear()` methods to free memory
   - Remove debug files when done

## 🤝 Integration with Existing Projects

To integrate with your existing LangGraph project:

1. Copy the `langgraph-debug` folder to your project
2. Import the modules in your graph definitions
3. Add debugging calls to your node functions
4. Run your graph as normal
5. Review the generated reports

## 📝 Custom Callbacks

You can add custom callbacks to react to debug events:

```python
def my_callback(event):
    if event['event_type'] == 'error':
        send_alert(event)
    elif event['event_type'] == 'timing':
        if event['duration_seconds'] > 5.0:
            log_slow_execution(event)

config = DebugConfig(
    level=DebugLevel.DEBUG,
    callbacks=[my_callback]
)
```

## 🐛 Troubleshooting

**Q: No debug output showing?**
- Check your debug level is high enough
- Ensure `console_output=True` in config

**Q: Token counts are zero?**
- Make sure to pass `input_tokens` and `output_tokens` to `end_node()`

**Q: Large memory usage?**
- Call `clear()` methods periodically
- Reduce `max_message_length` in config
- Enable `truncate_long_messages`

## 📄 License

This module is part of your LangGraph project.

## 🚀 Next Steps

1. Run the basic example to see the toolkit in action
2. Integrate debugging into your own graphs
3. Experiment with different debug levels
4. Generate HTML reports for stakeholders
5. Set up production monitoring

---

**Happy Debugging! 🎉**

For questions or issues, please refer to the examples or check the inline documentation in each module.
