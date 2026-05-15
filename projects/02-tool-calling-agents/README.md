# Tool Calling Agents

## Overview

Building LLM agents that can:
- call tools
- maintain memory
- route intent
- persist state
- evaluate tool selection accuracy

## Concepts Covered

- function/tool calling
- agent orchestration
- checkpoint memory
- SQLite persistence
- deterministic evaluation
- LLM-as-judge evaluation

## Implementations

### Weather Agent
Simple tool that returns weather for a given city. Demonstrates basic tool definition and invocation.

### Calculator Agent
Mathematical expression evaluator using `eval` with restricted builtins for safety.

### Medical Routing Agent
Multi-tool agent that routes user queries to appropriate medical tools:
- `search_symptoms` - symptom lookup
- `suggest_specialist` - care recommendation
- `analyze_medical_report` - report analysis

### Doc QA Agent
Document-based question answering with retrieval and evaluation.

## Evaluation Results

### Baseline Metrics

| Metric | Value |
|--------|-------|
| Tool Accuracy | 75% |
| Judge Agreement | 100% |

### Improvement Targets

| Stage | Target | Status |
|-------|--------|--------|
| Baseline | 75% | Complete |
| V1 | 80% | Planned |
| V2 | 85% | Planned |
| Target | >90% | In Progress |

### Test Breakdown

| Difficulty | Count | Focus |
|------------|-------|-------|
| Easy | 5 | Direct tool calls |
| Medium | 4 | Indirect routing |
| Hard | 4 | Ambiguous cases |
| Edge | 3 | No-tool scenarios |

## Project Structure

```
tool-calling-agents/
├── src/
│   ├── agents/         # Agent implementations
│   ├── tools/          # Tool definitions
│   ├── memory/         # Checkpointing logic
│   └── evaluation/     # Evaluation scripts
├── notebooks/          # Exploratory notebooks
├── tests/              # Unit tests
├── examples/           # Usage examples
├── outputs/            # Evaluation results
└── requirements.txt
```

## Setup

```bash
uv sync
uv sync --extra agents  # for agent features
uv sync --extra eval    # for evaluation features
uv sync --extra all     # everything
```

## Usage

### In-Memory Agent

```bash
python -m src.agents.inmemory_agent
```

### SQLite Agent (Persistent)

```bash
python -m src.agents.sqlite_agent
```

### Run Evaluation

```bash
python -m src.evaluation.tool_calling_evaluation
```

### Medical Routing Demo

```bash
python -c "from src.agents import create_inmemory_agent; agent = create_inmemory_agent(); print(agent.invoke({'messages': [{'role': 'user', 'content': 'I have headaches for 3 days'}]}))"
```

## Lessons Learned

1. Tool naming matters - descriptive names improve routing accuracy
2. System prompts significantly affect tool selection behavior
3. Checkpointing enables conversation continuity across sessions
4. SQLite persistence allows agent state to survive restarts
5. LLM-as-judge catches edge cases that deterministic metrics miss

## Future Improvements

- Add more tool variety for complex routing scenarios
- Implement multi-turn tool chains (tool calling tool results)
- Add latency tracking for tool execution
- Integrate with LangGraph for more sophisticated orchestration
