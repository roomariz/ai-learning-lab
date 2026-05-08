# How to Add a Custom Node

QueryFlow is designed to be extensible. You can create custom nodes by subclassing the base `Node` class.

## Basic Custom Node

```python
from query_flow import Node, Pipeline

class MyNode(Node):
    def run(self, input_data):
        # Your processing logic here
        return input_data.upper()  # Example: uppercase the input

    def explain(self):
        return {
            "node_name": self.name,
            "processing_summary": "Transformed input to uppercase"
        }

# Use it in a pipeline
flow = Pipeline("my-pipeline")
flow.add_node("upper", MyNode)
result = flow.run("hello")
print(result)  # "HELLO"
```

## Advanced Custom Node with Scoring

```python
from query_flow import Node, Pipeline

class BoostNode(Node):
    """Node that boosts documents containing specific terms."""
    
    def __init__(self, name: str, **params):
        super().__init__(name, **params)
        self.boost_terms = params.get("boost_terms", [])
        self.boost_factor = params.get("boost_factor", 1.5)

    def run(self, input_data):
        if not isinstance(input_data, list):
            return input_data
        
        boosted = []
        for item in input_data:
            score = item.get("score", 0)
            text = item.get("text", "").lower()
            
            for term in self.boost_terms:
                if term.lower() in text:
                    score *= self.boost_factor
            
            boosted.append({**item, "score": score})
        
        return sorted(boosted, key=lambda x: x["score"], reverse=True)

    def explain(self):
        return {
            "node_name": self.name,
            "processing_summary": f"Boosted docs containing: {self.boost_terms}",
            "boost_factor": self.boost_factor
        }

# Use it
flow = Pipeline("boost-pipeline")
flow.add_node("booster", BoostNode, boost_terms=["einstein", "physics"], boost_factor=2.0)

data = [
    {"text": "About Albert Einstein", "score": 0.5},
    {"text": "About Marie Curie", "score": 0.6}
]
result = flow.run(data)
```

## Node Interface

Your custom node must implement:

| Method | Required | Description |
|--------|----------|-------------|
| `run(input_data)` | Yes | Process input and return output |
| `explain()` | Yes | Return dict with node explanation |
| `__init__(name, **params)` | Yes | Initialize with name and parameters |

The `explain()` method should return a dict like:

```python
{
    "node_name": "my_node",
    "processing_summary": "What the node did",
    "metadata": {...}  # optional additional info
}
```

## Full Example: Custom RAG Node

```python
from query_flow import Node
import requests

class CustomRAGNode(Node):
    """Custom RAG node that formats context for LLM."""
    
    def __init__(self, name: str, **params):
        super().__init__(name, **params)
        self.max_context = params.get("max_context", 2000)
        self.format = params.get("format", "context: {text}")

    def run(self, input_data):
        if not isinstance(input_data, list):
            return "No context available"
        
        context_parts = []
        total_len = 0
        
        for item in input_data:
            text = item.get("text", "")[:200]  # Truncate each
            if total_len + len(text) > self.max_context:
                break
            context_parts.append(self.format.format(text=text))
            total_len += len(text)
        
        return "\n\n".join(context_parts)

    def explain(self):
        return {
            "node_name": self.name,
            "processing_summary": f"Formatted {len(input_data) if isinstance(input_data, list) else 0} docs as context",
            "max_context": self.max_context
        }

# Use in pipeline
flow = Pipeline()
flow.add_node("rag", CustomRAGNode, max_context=1000, format="Document: {text}")
result = flow.run([{"text": "Some document content"}])
```

## Tips

1. **Always handle edge cases**: Check if input is None, empty list, or wrong type
2. **Use `self.params`**: Access configuration via `self.params.get("key", default)`
3. **Return meaningful explanations**: Helps with debugging and trace
4. **Test incrementally**: Use `flow.run(..., debug=True)` to inspect behavior