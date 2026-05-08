# QueryFlow

**Explainable Retrieval + Query Orchestration Engine**

Deterministic filtering followed by similarity-based ranking, with layered, auditable explanations.

Scores must be interpreted within a single query context only; they are not absolute and must not be compared across queries.

Every result tells you *why* it was returned. Deterministic, reproducible, built-in evaluation.

## Install & Run (60 seconds)
Core install is lightweight. Advanced features require optional extras.
For local development or running the Streamlit app, install:

```bash
pip install -r requirements-dev.txt
pip install -e '.[retrieval,yaml,benchmark]'
uv pip install -e '.[retrieval,yaml,benchmark]'
```

## Quick Check: End-To-End Retrieval

Run this one-command smoke test to validate the basic retrieval path:

```bash
python scripts/smoke_test.py
```

It performs:

- dataset load
- retriever initialization
- a single query
- printed results

If you only need one optional feature set:

```bash
pip install -e '.[retrieval]'
pip install -e '.[yaml]'
pip install -e '.[benchmark]'
```

```python
from query_flow import check
from query_flow import pipelines

# Health check first
check()

# Simple query - works out of the box
result = pipelines.statistical().run("famous scientists")
debug_result = pipelines.statistical().run("famous scientists", debug=True)

for r in debug_result.results[:2]:
    print(r["doc_id"], "- Score:", round(r["score"], 2), "(relative ranking score)")
```

**Output:**
```
doc_002 - Score: 0.47 (relative ranking score)
doc_001 - Score: 0.46 (relative ranking score)
```

## Explainability First

Every result includes a structured explanation of why it was returned:

```python
result = pipelines.statistical().run(
    "Find people whose first name starts with A", debug=True
)

# The UI renders:
```

**Output:**
```
Main reason: Rule-based filtering
Dominant factor: Rule-based filtering
Secondary signal: Semantic similarity
Signals:
- Semantic similarity: 0.63
- Keyword relevance: 1.00
Constraints:
- Rule applied: Yes (constraint matched)
- Metadata condition: No
```

The UI derives these labels from the underlying explanation scores.

The UI shows:
- **Main reason**: Bold, directly under score
- **Dominant factor**: The main contributor to the result
- **Secondary signal**: Any supporting signal
- **System behaviour**: A short summary of the active retrieval signals

## Why QueryFlow?

| Capability | QueryFlow | Typical RAG |
|------------|-----------|-------------|
| **Hybrid retrieval** (dense + BM25) | Yes | Partial |
| **Query understanding** (type detection) | Yes | No |
| **Rule-based filtering** | Yes | No |
| **Metadata reasoning** | Yes | No |
| **Explainability** (per-result breakdown) | Yes | No |
| **Deterministic output** (seed support) | Yes | Rare |
| **Built-in evaluation** | Yes | Rare |

## Benchmark Results

Run `benchmark.run_default()` on sample dataset:

Benchmark modes reflect actual retrieval strategies implemented in the codebase.

| Method | Precision@5 |
|--------|-------------|
| Dense | 0.33 |
| BM25 | 0.44 |
| Hybrid | 0.33 |
| Statistical | **0.78** |

Statistical retrieval combines dense, BM25, rule-based, and metadata scoring to improve ranking quality.

Note: Scores depend on dataset size and query complexity. Larger datasets show clearer gains from statistical selection.

## Example: Why This Result?

**Query:** "Find people not born in Europe but active in 20th century"

**Result:**
```
Albert Einstein
Score: 0.91 (relative ranking score)

Why:
- Semantic match (dense): 0.75
- Metadata match: 1.0
- Constraints: lived in 20th century, born before 1900
- Rule applied: Yes (constraint matched)
```

This is QueryFlow's strongest feature: every result comes with a clear explanation of why it was returned.

## Demo

Try these queries to see QueryFlow in action:

```python
from query_flow import pipelines

# Rule activation - "Names starting with A"
result = pipelines.statistical().run(
    "Find people whose first name starts with A", debug=True
)
# → Rule applied: Yes (constraint matched)

# Metadata activation - "20th century constraint"  
result = pipelines.statistical().run("Find people active in the 20th century but born before 1900", debug=True)
# → Metadata condition: Triggered

# Logical rewrite
result = pipelines.statistical().run("Find people not born in Europe", debug=True)
# → Query rewritten: people born outside europe
```

Scores reflect similarity-based ranking applied only after all deterministic filters have been satisfied.

### Streamlit UI

Run `streamlit run app.py` for interactive demo with:
- Example query buttons
- Score breakdown visualization
- Query understanding section
- Pipeline trace

## Use Cases

### Legal Search
Find cases with constraints that typical RAG cannot handle:
- "Cases not decided in UK but relevant to asylum law"
- Filter by jurisdiction, date, and topic simultaneously

### Compliance Queries
Time + condition logic for audit scenarios:
- "Documents from Q3 2024 that mention risk but not mitigation"
- Deterministic reproduction for audit trails

### Enterprise Search
Debuggable retrieval for internal knowledge bases:
- See exactly which scoring component contributed most
- Trace query type detection and rewrite decisions

## Core Concepts

### 1. Pipelines

```python
from query_flow import pipelines

# Best for most cases: retrieval + query analysis
flow = pipelines.rag(k=5)

# Pure statistical retrieval
flow = pipelines.statistical(k=5)

# Hybrid dense + BM25
flow = pipelines.hybrid(k=5)

# Legal domain search
flow = pipelines.legal_search(k=5)
```

### 2. Debug

```python
flow = pipelines.statistical()

result = flow.run("famous scientists", debug=True)

# Access all details
print(result.query)                          # Original query
print(result.debug_info["query_analysis"])   # Query type, rewritten query
print(result.trace)                          # Step-by-step execution
print(result.message)                        # Any warnings or info
```

Example output:
- Query type: Lexical (name constraint detected)
- System behaviour: Rule-based filters applied, then results ranked by semantic similarity
- Score: A relative ranking value used to order results within a single query. It is not an absolute measure and must not be compared across different queries.

### 3. Deterministic

```python
# Same seed = same results (critical for legal/compliance)
result1 = flow.run("query", seed=42)
result2 = flow.run("query", seed=42)

assert result1.results == result2.results  # Always true
```

### 4. Analyzer

```python
from query_flow import QueryAnalyzer

analysis = QueryAnalyzer.analyze("not born in europe")

print(analysis.query_type.value)     # "logical"
print(analysis.confidence)           # 0.9
print(analysis.suggested_retrieval)  # "Use dense retrieval with semantic matching"
```

### 5. Extension

```python
from query_flow import Node, Pipeline

class MyCustomNode(Node):
    def run(self, input_data):
        return input_data.upper()
    
    def explain(self):
        return {"node_name": self.name, "processing_summary": "Uppercased input"}

flow = Pipeline().add_node("upper", MyCustomNode)
```

See [docs/CUSTOM_NODES.md](docs/CUSTOM_NODES.md) for full guide.

### 6. Benchmarking

```python
from query_flow import benchmark

results = benchmark.run_default()
# Compares: dense vs bm25 vs hybrid vs smart vs statistical
```

### 7. Dataset Loading

```python
from query_flow import data
from query_flow import StatisticalRetriever

# From list
ds = data.Dataset.from_list([{"id": "1", "text": "..."}])

# From file
ds = data.Dataset.from_json("docs.json")
ds = data.Dataset.from_csv("docs.csv")

# Use with retriever
retriever = StatisticalRetriever()
retriever.set_documents(ds.documents)
```

## Architecture

```
Query → QueryAnalyzer → Retrieval (Dense + BM25 + Rules + Metadata) → Ranking → Results
       ↓                                                             ↓
  Query Type                                                   Explainability
```

### Query Types

- **Semantic**: Natural language queries → dense retrieval
- **Lexical**: "starts with X" → rule-based filtering
- **Temporal**: "20th century" → metadata scoring
- **Logical**: "not X" or "X but Y" → semantic matching

## Evaluation Metrics

Built-in support for:
- Precision@k
- Recall@k
- F1@k
- MRR (Mean Reciprocal Rank)
- NDCG@k

## API Reference

### Pipeline

| Method | Description |
|--------|-------------|
| `add_node(name, type, **params)` | Add a node to pipeline |
| `connect(from, to)` | Connect nodes |
| `run(query, debug=False, seed=None)` | Execute pipeline |
| `print_trace()` | Visual trace output |

### QueryAnalyzer

| Method | Description |
|--------|-------------|
| `detect(query)` | Return query type string |
| `analyze(query)` | Full analysis with confidence |

### StatisticalRetriever

| Method | Description |
|--------|-------------|
| `retrieve(query, k=5)` | Return results with scores |
| `explain(query, k=5)` | Full explanations |

## License

MIT

## Repository

- Main: `query_flow/` - Core package
- Docs: `docs/CUSTOM_NODES.md` - Extension guide
- Examples: `query_flow/examples.py` - Demo usage
