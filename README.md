# AI Learning Lab

A monorepo for hands-on AI and machine learning engineering projects.

## Projects

| # | Project | Topic | Status | Live Demo |
|---|---------|-------|--------|-----------|
| 01 | `ai-agents/01-ollama-langsmith-react-tracing-agent` | Ollama ReAct agent tracing | Implemented | - |
| 02 | `ai-agents/02-ollama-local-agent-tracing` | Ollama local agent tracing | Implemented | - |
| 03 | `02-tool-calling-agents` | Agent tool calling | Evaluating: 75% → 90% target | - |
| 04 | `03-query-flow` | Query orchestration | Implemented | [Live demo](https://ai-learning-lab-03-query-flow.streamlit.app/) |
| 05 | `04-ragas-evaluation` | Evaluation and benchmarking | Benchmark baseline complete | - |
| 06 | `05-ai-dev-server` | AI developer tooling | Prototype complete | - |
| 07 | `06-rag-engineering-lab` | Retrieval-augmented generation pipelines | Implemented | - |
| 08 | `07-milvus-vector-store-lab` | Vector databases | Implemented | - |
| 09 | `08-ai-toolkit` | Tool-calling framework | Implemented | [Live demo](https://ollama-toolbox-demo.streamlit.app/) |
| 10 | `09-mcp-cli-project` | Model Context Protocol CLI and local LLM chat | Implemented | - |
| 11 | `10-mcp-lab` | Model Context Protocol and LangChain integration | Implemented | - |

## Project Summaries

### `ai-agents/01-ollama-langsmith-react-tracing-agent`

LangChain ReAct agent with Ollama and LangSmith tracing for inspecting model calls, tool calls, tool observations and final answers.

**Features**

- Local Ollama inference
- Renewable-energy dataset lookup
- Arithmetic tool
- LangSmith trace inspection
- ReAct flow

---

### `ai-agents/02-ollama-local-agent-tracing`

Local Ollama agent built with LangChain and LangGraph, focused on tool use, structured JSONL tracing and log rotation.

**Features**

- Local LLM execution
- Custom energy and arithmetic tools
- JSONL trace logging
- Daily rotation
- Seven-day retention

---

### `02-tool-calling-agents`

LLM agents with tool calling, memory and evaluation.

**Implementations**

- Weather Agent
- Calculator Agent
- Medical Routing Agent
- Document QA Agent

**Evaluation status**

- Baseline tool accuracy: 75%
- Target tool accuracy: above 90%

---

### `03-query-flow`

Explainable query orchestration engine using deterministic filtering followed by similarity-based ranking with layered, auditable explanations.

**Features**

- Hybrid retrieval using dense search and BM25
- Rule-based filtering
- Metadata reasoning
- Per-result explainability

---

### `04-ragas-evaluation`

RAG evaluation and benchmarking toolkit using Qdrant vector store and Ollama for local LLM inference.

**Features**

- RAGAS evaluation
- Faithfulness scoring
- Answer relevancy scoring
- Context precision and recall
- Chunking quality benchmarks
- Streamlit dashboard

---

### `05-ai-dev-server`

AI developer tooling CLI that generates, validates, runs and hot-reloads Express.js backends from natural language prompts.

**Features**

- Multi-file project generation
- Strict output validation
- Iterative refinement
- Watch and restart support

---

### `06-rag-engineering-lab`

RAG pipelines with LangChain, LangGraph and Ollama.

**Features**

- Multi-format loading, including HTML, PDF and CSV
- Configurable chunking
- Local LLM inference
- LangSmith tracing

---

### `07-milvus-vector-store-lab`

Traceable, citation-first document question-answering system with sentence-level precision.

**Features**

- Sentence-level retrieval
- Source traceability by page and section
- Verbatim citations
- Minimal context retrieval

---

### `08-ai-toolkit`

Tool-calling framework for Ollama with CLI and Streamlit interfaces, tool chaining, async execution, retry logic and structured logging.

**Features**

- Multiple tools
- Interactive CLI
- Streamlit UI
- JSON schema validation
- Async and parallel execution
- Tool chaining

---

### `09-mcp-cli-project`

Command-line chat client that connects to a local Ollama model and enriches responses with MCP tools, prompts and document resources.

**Features**

- Prompt-toolkit CLI
- `@doc_id` context injection
- MCP prompt execution
- Document resources
- Ollama chat wrapper

---

### `10-mcp-lab`

LangChain agent wired to a simple MCP math server, demonstrating MCP tool calling with Ollama.

**Features**

- FastMCP server with `add` and `multiply` tools
- LangChain MCP client
- Automatic model selection
- Iteration safety cap

## Setup

Each project is independent and maintains its own dependencies.

```bash
cd projects/<project-name>
```

For Python projects:

```bash
uv sync
```

For Node.js projects:

```bash
npm install
```

## Dependencies

* Python projects are managed with `uv`.
* Node.js projects use `npm`.
* Each project maintains its own virtual environment.
* There is currently no shared code between projects.
