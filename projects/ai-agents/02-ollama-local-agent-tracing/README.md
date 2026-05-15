# Ollama Local Agent with Tracing

A local AI agent built with LangChain and LangGraph that connects to Ollama for running LLMs locally, with comprehensive tracing and logging capabilities.

## Overview

This project demonstrates an AI agent that:
- Connects to a local Ollama instance for LLM inference
- Uses tool calling to answer questions (e.g., energy data retrieval and calculations)
- Logs all agent interactions to local JSONL files with automatic rotation

## Features

- **Local LLM**: Runs using Ollama (no cloud dependencies)
- **Tool-Based Agent**: Uses LangChain's agent with custom tools
- **Energy Data Tools**: Example tools for retrieving UK wind/solar generation metrics
- **Arithmetic Operations**: Perform divide, multiply, add, subtract on retrieved values
- **Local Tracing**: All agent traces logged to JSONL files with:
  - Timestamps
  - Trace IDs
  - Event types (user messages, tool calls, observations, final answers)
  - Automatic daily rotation with 7-day retention

## Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed and running locally

## Installation

```bash
cd projects/ai-agents/02-ollama-local-agent-tracing

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1` | Model to use |
| `OLLAMA_TEMPERATURE` | `0` | LLM temperature |

## Usage

```bash
python src/main.py
```

Example output:
```
Final answer:
The UK's wind generation is approximately 1.94 times higher than its solar generation.
Wind: 8,765 MW
Solar: 4,521 MW
Ratio (wind/solar): 1.94

Local trace ID: <uuid>
```

## Project Structure

```
02-ollama-local-agent-tracing/
├── examples/
│   └── sample-agent-trace.jsonl  # Sample trace (safe to commit)
├── logs/
│   └── .gitkeep                   # Runtime logs (not committed)
├── src/
│   ├── main.py          # Entry point
│   ├── agent.py         # Agent creation with system prompt
│   ├── tools.py         # Custom tools (energy metrics, arithmetic)
│   ├── tracing.py       # Local JSONL trace logging
│   └── config.py        # Configuration settings
├── pyproject.toml
└── README.md
```

> **Note**: Real logs are written to `logs/` and are gitignored (may contain sensitive data). A sample trace is provided in `examples/`.

## Available Tools

### get_energy_metric
Retrieves energy metric values.

| Metric | Value (MW) |
|--------|------------|
| `uk_wind_generation` | 8765 |
| `uk_solar_generation` | 4521 |

### compute_arithmetic
Performs arithmetic on two numbers.

Supported operations: `divide`, `multiply`, `add`, `subtract`

## Local Tracing (No LangSmith)

This project does **not** use LangSmith. It demonstrates local, production-style agent tracing through structured JSONL logs, capturing:

- Tool requests and arguments
- Tool observations (responses)
- Tool errors and recovery steps
- Final answers
- Full conversation context with trace IDs

## Trace Log Format

Traces are saved to `logs/agent-trace.jsonl` with each line as:

```json
{
  "timestamp": "2024-01-15T10:30:00+00:00",
  "trace_id": "uuid",
  "event_type": "tool_call_requested",
  "data": {...}
}
```

Event types:
- `trace_started` / `trace_completed`
- `user_message`
- `tool_call_requested`
- `tool_observation`
- `final_answer`

### Sample Log

Running the app creates logs under `logs/`. Example:

```jsonl
{"timestamp":"2026-05-15T13:38:30.185828+00:00","trace_id":"a4203685-7ea5-4bf1-95c7-fb1cec4d75b2","event_type":"trace_started","data":{"message_count":8}}
{"timestamp":"2026-05-15T13:38:30.185828+00:00","trace_id":"a4203685-7ea5-4bf1-95c7-fb1cec4d75b2","event_type":"tool_call_requested","data":{"step":2,"tool_name":"get_energy_metric","tool_args":{"metric_name":"uk_wind_generation"}}}
{"timestamp":"2026-05-15T13:38:30.185828+00:00","trace_id":"a4203685-7ea5-4bf1-95c7-fb1cec4d75b2","event_type":"tool_observation","data":{"step":3,"tool_name":"get_energy_metric","tool_output":"{\"metric_name\":\"uk_wind_generation\",\"value\":8765,\"unit\":\"MW\"}"}}
{"timestamp":"2026-05-15T13:38:30.185828+00:00","trace_id":"a4203685-7ea5-4bf1-95c7-fb1cec4d75b2","event_type":"trace_completed","data":{"message_count":8}}
```

A fuller example is available in `examples/sample-agent-trace.jsonl`.
