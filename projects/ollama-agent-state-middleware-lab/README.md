# Ollama Agent State & Middleware Lab

A hands-on learning lab for agent state, tool state, runtime context, persistence, and middleware patterns using Ollama.

The project is local-first. Ollama is the default model provider, with optional OpenRouter support through environment variables.

## Structure

```txt
.
├── pyproject.toml
├── .env.example
├── README.md
├── src/
│   ├── common/
│   │   ├── config.py
│   │   ├── model.py
│   │   ├── printer.py
│   │   └── utils.py
│   │
│   ├── part_01_state_foundations/
│   │   ├── lab_01_messages_only_memory/
│   │   ├── lab_02_agent_state_intro/
│   │   ├── lab_03_custom_state/
│   │   ├── lab_04_model_provider_setup/
│   │   └── lab_05_state_persistence/
│   │
│   ├── part_02_tools_and_runtime/
│   │   ├── lab_06_tool_state_read_write/
│   │   ├── lab_07_tool_state_challenge/
│   │   ├── lab_08_toolruntime_solution/
│   │   ├── lab_09_reading_state_in_tools/
│   │   ├── lab_10_writing_state_from_tools/
│   │   └── lab_11_context_vs_state/
│   │
│   ├── part_03_langgraph_capstone/
│   │   ├── lab_12_production_ready_agents/
│   │   └── lab_13_bug_tracker_agent_langgraph/
│   │
│   └── part_04_middleware/
│       ├── lab_14_middleware_concept/
│       ├── lab_15_middleware_hooks/
│       ├── lab_16_input_validation_middleware/
│       ├── lab_17_tool_authorisation/
│       ├── lab_18_error_handling_middleware/
│       ├── lab_19_builtin_middleware/
│       └── lab_20_middleware_execution_order/
│   └── part_05_production_middleware/
            ├── lab_21_learning_agent_baseline/
            ├── lab_22_tool_authorisation_middleware/
            ├── lab_23_error_handling_middleware/
            ├── lab_24_message_trimming_middleware/
            ├── lab_25_logging_middleware/
            ├── lab_26_complete_production_learning_agent/
            └── lab_27_interactive_production_learning_agent/
└── data/
    └── state/
```

## Labs by Part

### Part 1: State Foundations (Labs 01-05)

| Lab | Topic                    | Purpose                                                     |
| --: | ------------------------ | ----------------------------------------------------------- |
|  01 | Messages-only memory     | Shows why relying only on message history is weak           |
|  02 | Agent state intro        | Introduces structured state                                 |
|  03 | Custom state             | Tracks learner profile, progress, topic, and last action    |
|  04 | Model provider setup     | Adds a provider switch for Ollama and optional OpenRouter   |
|  05 | State persistence        | Saves and loads state from JSON                             |

### Part 2: Tools and Runtime (Labs 06-11)

| Lab | Topic                    | Purpose                                                     |
| --: | ------------------------ | ----------------------------------------------------------- |
|  06 | Tool state read/write    | Shows tools reading and writing state manually              |
|  07 | Tool state challenge     | Shows why manual state passing becomes fragile              |
|  08 | ToolRuntime solution     | Introduces a runtime object for state and context           |
|  09 | Reading state in tools   | Shows read-only tool access to state                        |
|  10 | Writing state from tools | Shows controlled state mutation from tools                  |
|  11 | Context vs state         | Separates stable runtime context from changing state        |

### Part 3: LangGraph Capstone (Labs 12-13)

| Lab | Topic                       | Purpose                                                     |
| --: | --------------------------- | ----------------------------------------------------------- |
|  12 | Production-ready agents     | Adds validation, authorisation, blocking, and observability |
|  13 | Bug tracker agent LangGraph | Full bug tracker with LangGraph                              |

### Part 4: Middleware (Labs 14-20)

| Lab | Topic                        | Purpose                                                     |
| --: | ---------------------------- | ----------------------------------------------------------- |
|  14 | Middleware concept           | Moves production controls into middleware-style functions   |
|  15 | Middleware hooks             | Pre/post tool execution hooks                               |
|  16 | Input validation middleware  | Validates user input before tools                          |
|  17 | Tool authorisation           | Controls which tools users can call                        |
|  18 | Error handling middleware    | Catches and handles tool errors                            |
|  19 | Builtin middleware           | Reusable middleware components                             |
|  20 | Middleware execution order   | Controls middleware execution order                         |

### Part 5: Production Middleware (Labs 21-27)

| Lab | Topic | Purpose |
| --: | ----- | ------- |
| 21 | Learning agent baseline | Baseline learning agent without middleware |
| 22 | Tool authorisation middleware | Blocks premium tools for free users |
| 23 | Error handling middleware | Handles tool failures safely |
| 24 | Message trimming middleware | Keeps recent messages and trims old context |
| 25 | Logging middleware | Adds observability around model and tool execution |
| 26 | Complete production learning agent | Composes all middleware layers |
| 27 | Interactive production learning agent | Runs the production agent in terminal chat |

## Prerequisites

Install and run Ollama locally:

```bash
ollama serve
```

## Recommended Ollama Models

This lab is designed to work best with a small local model set:

| Model | Purpose |
|---|---|
| `qwen3:14b` | Main agent model for LangChain agents, tool calling, reasoning, and middleware labs |
| `qwen2.5-coder:7b` | Coding-focused model for debugging, refactoring, and code generation |
| `nomic-embed-text` | Embedding model for retrieval and RAG workflows |

## Install Models

```bash
ollama pull qwen3:14b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

Confirm the model is available:

```bash
ollama list
```

For more details (including how to wire these models into `.env`), see `docs/model_setup.md`.

## Setup with uv

```bash
uv sync
cp .env.example .env
```

On Windows PowerShell, if `cp` is unavailable:

```powershell
Copy-Item .env.example .env
```

## Environment

Default local setup:

```env
MODEL_PROVIDER=ollama

OLLAMA_MODEL=qwen3:14b
OLLAMA_CODER_MODEL=qwen2.5-coder:7b
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434

OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Run labs with taskipy

Each lab has its own `README.md`, `main.py`, and `expected_output.txt`.

```bash
uv run task lab01
uv run task lab05
uv run task lab13
```

To see all available tasks:

```bash
uv run task --list
```

To run a specific lab directly without taskipy:

```bash
uv run python -m src.part_01_state_foundations.lab_01_messages_only_memory.main
```

## Local state files

Lab 05 creates local persisted state:

```txt
data/state/learning_state.json
```

This file should not be committed. Keep it ignored:

```gitignore
data/state/*.json
```

## Learning path

The labs are designed to build step by step:

```txt
Message history
→ structured state
→ custom state
→ persistence
→ tools reading and writing state
→ runtime context
→ production controls
→ middleware
→ production middleware composition
→ interactive production agent
```

## Design principle

The model should not be responsible for everything.

Production-style agents need deterministic application controls around the model, including validation, authorisation, controlled state mutation, observability, and error handling.

## Agent build reference

For future labs and agent implementations, follow `docs/stateful_agent_blueprint.md` as the reference pattern.

Use the same `AgentState`, `ToolRuntime`, `Command(update={...})`, `ToolMessage`, `MemorySaver`, thread-based persistence, and clean interactive structure unless there is a clear reason not to.
