# AI Learning Lab

A monorepo for hands-on AI/ML engineering learning projects.

## Current Structure

```
ai-learning-lab/
├── projects/
│   ├── 01-rag-retrieval-lab/     # Placeholder (not started)
│   └── 07-tool-calling-agents/  # Active project
├── README.md
└── .gitignore
```

## Projects

| Project | Topic | Status |
|---------|-------|--------|
| 01-rag-retrieval-lab | RAG & Retrieval | Not Started |
| 07-tool-calling-agents | Tool Calling & Agents | In Progress |

## Active Project: 07-tool Calling Agents

Building LLM agents with:
- Tool/function calling
- Agent orchestration
- Checkpoint memory (in-memory & SQLite)
- Deterministic & LLM-as-judge evaluation

### Concepts Covered
- function/tool calling
- agent orchestration
- checkpoint memory
- SQLite persistence
- deterministic evaluation
- LLM-as-judge evaluation

### Implementations
- **Weather Agent** - basic tool definition and invocation
- **Calculator Agent** - mathematical expression evaluator
- **Medical Routing Agent** - multi-tool query routing
- **Doc QA Agent** - document-based Q&A with retrieval

### Setup

```bash
cd projects/07-tool-calling-agents
uv sync
```

### Usage

```bash
cd projects/07-tool-calling-agents

# Install dependencies
uv sync

# Import test (verifies modules load)
python -c "from src.agents.inmemory_agent import create_inmemory_agent; print('OK')"
python -c "from src.agents.sqlite_agent import create_sqlite_agent; print('OK')"

# Run interactive agent (requires Ollama)
python -m src.agents.inmemory_agent

# Run evaluation (requires model API)
python -m src.evaluation.tool_calling_evaluation
```

## Roadmap

- [ ] 01-rag-retrieval-lab
- [x] 07-tool-calling-agents

## Notes

- Dependencies managed with `uv`
- Each project maintains its own virtual environment
- No shared/ reusable code yet (projects are isolated)