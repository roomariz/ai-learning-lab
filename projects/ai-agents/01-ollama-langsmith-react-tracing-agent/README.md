# Ollama LangChain ReAct Agent with LangSmith Tracing

A small LangChain ReAct agent using Ollama for local Large Language Model inference and LangSmith for tracing and observability.

## Overview

This project demonstrates a tool-calling agent that:

- Uses the `llama3.1` model through Ollama for local inference
- Uses LangChain's agent API for tool calling
- Retrieves values from a local renewable-energy dataset
- Performs a calculation through a separate arithmetic tool
- Sends traces to LangSmith so the model calls, tool calls and tool observations can be inspected

The example query asks the agent to compare the United Kingdom's wind generation with its solar generation and calculate the ratio as:

```text
wind generation / solar generation
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.12 or later
- `uv` installed
- Ollama installed
- The `llama3.1` model pulled locally
- A LangSmith account and API key

Pull the Ollama model:

```bash
ollama pull llama3.1
```

Make sure Ollama is running:

```bash
ollama serve
```

If Ollama is already running, you can ignore the "address already in use" message.

## Setup

Install dependencies:

```bash
uv sync
```

Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your LangSmith settings:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=ollama-react-agent
```

For the EU LangSmith endpoint, use:

```env
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

## Running the Agent

Run the project from this project directory:

```bash
uv run python src/main.py
```

The agent will:

1. Receive a user query about UK wind and solar generation
2. Decide which tools are required
3. Call `get_energy_metric` to retrieve the wind generation value
4. Call `get_energy_metric` to retrieve the solar generation value
5. Call `compute_arithmetic` to calculate the ratio
6. Print the final answer, tool calls and tool observations
7. Send the trace to LangSmith for inspection

## Tools

### `get_energy_metric`

Retrieves a renewable-energy metric from a local dataset.

Available example keys:

```text
uk_wind_generation_gwh
uk_solar_generation_gwh
spain_wind_generation_gwh
spain_solar_generation_gwh
```

### `compute_arithmetic`

Safely evaluates a simple arithmetic expression.

Example:

```text
82300 / 14900
```

The implementation uses Python's `ast` module rather than raw `eval()`, so only simple arithmetic expressions are supported.

## Example Output

```text
Final answer:
The ratio of UK's wind generation to its solar generation is approximately 5.52.

Tool calls:
- get_energy_metric: {'metric_name': 'uk_wind_generation_gwh'}
- get_energy_metric: {'metric_name': 'uk_solar_generation_gwh'}
- compute_arithmetic: {'expression': '82300 / 14900'}

Tool observations:
- get_energy_metric: 82300
- get_energy_metric: 14900
- compute_arithmetic: 5.52
```

## LangSmith Trace

After running the script, open LangSmith and select the project configured in `.env`:

```env
LANGSMITH_PROJECT=ollama-react-agent
```

In the trace, you should see the agent flow:

```text
User message
↓
Model call
↓
Tool call: get_energy_metric
↓
Tool observation: 82300
↓
Tool call: get_energy_metric
↓
Tool observation: 14900
↓
Tool call: compute_arithmetic
↓
Tool observation: 5.52
↓
Final model answer
```

Depending on the model behaviour, multiple tool calls may appear in the same model step. That is still valid. The important point is that the trace shows the separation between model reasoning, tool execution, observations and final answer.

## Project Structure

```text
01-ollama-langsmith-react-tracing-agent/
├── src/
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Environment Variables

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=ollama-react-agent
```

Optional Ollama-related variables can be added later if the project is split into a larger configuration structure, but the current script uses:

```python
model="llama3.1"
temperature=0
```

directly inside `src/main.py`.

## Performance Notes

Local Ollama execution may be slower than a hosted API, especially on the first run.

The first run is usually slower because the model is loaded into memory. Subsequent runs are normally faster while Ollama remains active.

For more stable local behaviour:

- Keep the system prompt concise
- Use `temperature=0`
- Keep Ollama running between runs
- Avoid setting the recursion limit too low

A very low recursion limit, such as `5`, may stop the agent before it reaches a final answer and can cause a `GraphRecursionError`.

A safer invocation, if you want to set a limit, is:

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Compare the UK's wind generation with its solar generation. "
                    "Calculate wind divided by solar."
                ),
            }
        ]
    },
    config={"recursion_limit": 12},
)
```

The current working version can also run without setting a custom recursion limit.

## Notes

This project is for learning and inspection of ReAct-style tool use with LangSmith tracing.

The dataset is local and intentionally small. It is not intended to represent live energy statistics.

The arithmetic tool is suitable for a learning exercise. For production, prefer structured tool arguments such as:

```python
compute_arithmetic(operation="divide", a=82300, b=14900)
```

rather than asking the model to construct a string expression.

## Suggested Commit Message

```text
Add Ollama LangSmith ReAct tracing example
```
