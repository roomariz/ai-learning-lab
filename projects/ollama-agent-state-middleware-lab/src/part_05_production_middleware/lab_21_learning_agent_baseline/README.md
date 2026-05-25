# 21 Learning Agent Baseline

**Purpose:** Build the simplest working Ollama-powered learning agent with
LangChain `create_agent()` — no middleware yet.

**Why first:** Part 05 follows the progression *baseline → add one middleware →
add another → final production stack*. This is the zero point.

**Teaching objective:** Learn how a plain LangChain agent behaves before
middleware controls are introduced.

**Agent flow:** User prompt → LLM chooses tool → tool returns result → LLM produces final assistant answer.

**Key lesson:** Without middleware:
- Premium tools are freely accessible
- No validation, logging, retries, trimming, or production safety

## Files

| File | Purpose |
|------|---------|
| `app.py` | Agent creation and invocation |
| `tools.py` | Re-export of the shared learning tools |
| `expected_output.md` | Sample console output |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_21_learning_agent_baseline.app
```
