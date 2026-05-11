# AI Learning Lab

A monorepo for hands-on AI/ML engineering learning projects.

## Projects

| # | Project | Topic | Status | Live Demo |
|---|---------|-------|--------|-----------|
| 02 | 02-tool-calling-agents | Agent Tool Calling | Evaluating (75% → 90% target) | [README](projects/02-tool-calling-agents/README.md) |
| 03 | 03-query-flow | Query Orchestration | Implemented | https://ai-learning-lab-03-query-flow.streamlit.app/ |
| 04 | 04-ragas-evaluation | Evaluation & Benchmarking | Benchmark Baseline Complete | [README](projects/04-ragas-evaluation/README.md) |
| 05 | 05-ai-dev-server | AI Developer Tooling | Prototype Complete | [README](projects/05-ai-dev-server/README.md) |
| 06 | 06-rag-engineering-lab | RAG Pipelines | Implemented | [README](projects/06-rag-engineering-lab/README.md) |
| 07 | 07-milvus-vector-store-lab | Vector Databases | Implemented | [README](projects/07-milvus-vector-store-lab/README.md) |
| 08 | 08-ai-toolkit | Tool-Calling Framework | Implemented | https://ollama-toolbox-demo.streamlit.app/ |
| 09 | 09-mcp-cli-project | MCP CLI + local LLM chat | In Progress | [README](projects/09-mcp-cli-project/README.md) |

## Project Summaries

### 02-tool-calling-agents
Building LLM agents with tool calling, memory (in-memory & SQLite), and evaluation (deterministic & LLM-as-judge).

**Implementations:** Weather Agent, Calculator Agent, Medical Routing Agent, Doc QA Agent

**Status:** Baseline 75% tool accuracy, targeting >90%

### 03-query-flow
Explainable query orchestration engine. Deterministic filtering followed by similarity-based ranking with layered, auditable explanations.

**Features:** Hybrid retrieval (dense + BM25), rule-based filtering, metadata reasoning, per-result explainability

### 04-ragas-evaluation
RAG evaluation & benchmarking toolkit with Qdrant vector store and Ollama for local LLM inference.

**Features:** RAGAs evaluation (faithfulness, answer relevancy, context precision/recall), chunking quality benchmarks, Streamlit dashboard

### 05-ai-dev-server
AI developer tooling - CLI tool that generates, validates, runs, and hot-reloads Express.js backends from natural language prompts.

**Features:** Multi-file project generation, strict output validation, iterative refinement, watch/restart

### 06-rag-engineering-lab
RAG pipelines with LangChain, LangGraph, and Ollama.

**Features:** Multi-format loading (HTML/PDF/CSV), configurable chunking, local LLM inference, LangSmith tracing

### 07-milvus-vector-store-lab
Vector databases - traceable, citation-first document Q&A system with sentence-level precision.

**Features:** Sentence-level retrieval, source traceability (page/section), verbatim citations, minimal context

### 08-ai-toolkit
Tool-calling framework for Ollama with CLI and Streamlit interfaces, tool chaining, async execution, retry logic, and structured logging.

**Features:** Multiple tools, interactive CLI, Streamlit UI, JSON schema validation, async/parallel execution, tool chaining

### 09-mcp-cli-project
Command-line chat client that connects to a local Ollama model and enriches responses with MCP tools, prompts, and document resources.

**Features:** Prompt-toolkit CLI, `@doc_id` context injection, MCP prompt execution, document resources, Ollama chat wrapper

## Setup

Each project is independent with its own dependencies:

```bash
cd projects/<project-name>
# Python projects: uv sync
# Node projects: npm install
```

## Dependencies

- **Python projects**: managed with `uv`
- **Node projects**: use `npm`

Each project maintains its own virtual environment; no shared code yet.
