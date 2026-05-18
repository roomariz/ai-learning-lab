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
│   ├── 01_messages_only_memory/
│   ├── 02_agent_state_intro/
│   ├── 03_custom_state/
│   ├── 04_model_provider_setup/
│   ├── 05_state_persistence/
│   ├── 06_tool_state_read_write/
│   ├── 07_tool_state_challenge/
│   ├── 08_toolruntime_solution/
│   ├── 09_reading_state_in_tools/
│   ├── 10_writing_state_from_tools/
│   ├── 11_context_vs_state/
│   ├── 12_production_ready_agents/
│   └── 13_middleware_concept/
└── data/
    └── state/
```

## Completed labs

| Lab | Topic                    | Purpose                                                     |
| --: | ------------------------ | ----------------------------------------------------------- |
|  01 | Messages-only memory     | Shows why relying only on message history is weak           |
|  02 | Agent state intro        | Introduces structured state                                 |
|  03 | Custom state             | Tracks learner profile, progress, topic, and last action    |
|  04 | Model provider setup     | Adds a provider switch for Ollama and optional OpenRouter   |
|  05 | State persistence        | Saves and loads state from JSON                             |
|  06 | Tool state read/write    | Shows tools reading and writing state manually              |
|  07 | Tool state challenge     | Shows why manual state passing becomes fragile              |
|  08 | ToolRuntime solution     | Introduces a runtime object for state and context           |
|  09 | Reading state in tools   | Shows read-only tool access to state                        |
|  10 | Writing state from tools | Shows controlled state mutation from tools                  |
|  11 | Context vs state         | Separates stable runtime context from changing state        |
|  12 | Production-ready agents  | Adds validation, authorisation, blocking, and observability |
|  13 | Middleware concept       | Moves production controls into middleware-style functions   |

## Upcoming labs

```txt
14_middleware_hooks
15_input_validation_middleware
16_tool_authorisation
17_error_handling_middleware
18_builtin_middleware
19_middleware_execution_order
```

## Prerequisites

Install and run Ollama locally:

```bash
ollama serve
```

Pull a local model:

```bash
ollama pull qwen2.5-coder:7b
```

Confirm the model is available:

```bash
ollama list
```

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

OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434

OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Run labs with uv

Run one lab:

```bash
uv run python -m src.01_messages_only_memory.main
```

Examples:

```bash
uv run python -m src.05_state_persistence.main
uv run python -m src.08_toolruntime_solution.main
uv run python -m src.13_middleware_concept.main
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
```

## Design principle

The model should not be responsible for everything.

Production-style agents need deterministic application controls around the model, including validation, authorisation, controlled state mutation, observability, and error handling.