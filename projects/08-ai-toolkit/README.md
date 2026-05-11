# AI Toolkit

Tool-calling framework for building LLM apps with Ollama. The project includes a command-line interface, a Streamlit demo, tool chaining, async execution, retry logic, and structured logging.

## Live Demo

- Streamlit app: https://ollama-toolbox-demo.streamlit.app/

## Features

- Multiple tools: `search_docs`, `read_document`, `summarise_document`, `extract_keywords`, `answer_question`, `get_chuck_norris_fact`
- Interactive CLI
- Streamlit UI with a tool explorer
- JSON schema validation before execution
- Structured JSON logging
- Retry logic with exponential backoff
- Async and parallel tool execution
- Multi-step tool chaining

## Requirements

- Python 3.8+
- Ollama running locally at `http://localhost:11434`
- A model pulled in Ollama, for example `llama3.1:latest`

## Installation

### Using uv

```bash
cd projects/08-ai-toolkit
uv venv
source .venv/bin/activate
uv sync
```

### Using pip

```bash
cd projects/08-ai-toolkit
python -m venv .venv
source .venv/bin/activate
pip install ollama rich jsonschema requests streamlit pytest
```

## Configuration

Set environment variables or update [`src/config.py`](src/config.py):

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `llama3.1:latest` | Model name used by the tool-calling runtime |

Other settings in [`src/config.py`](src/config.py):

- `max_iterations` - Maximum tool call iterations
- `timeout` - Request timeout in seconds
- `retry_attempts` - Retry count for failed requests
- `retry_delay` - Delay between retries

## Usage

### Streamlit demo

```bash
streamlit run app.py
```

Open the URL shown by Streamlit, typically `http://localhost:8501`.

### CLI

```bash
python src/cli.py
```

### Batch run

```bash
python src/run_tools.py
```

### Tests

```bash
pytest tests/ -v
```

## Example prompts

- `Search docs for Python`
- `Tell me a Chuck Norris fact`
- `Extract keywords from machine learning`
- `Read document 123`
- `Summarise document 456`

## Project Structure

```text
projects/08-ai-toolkit/
├── app.py
├── pyproject.toml
├── src/
│   ├── async_runner.py
│   ├── chain.py
│   ├── cli.py
│   ├── config.py
│   ├── functions.py
│   ├── logger.py
│   ├── run_tools.py
│   ├── tools_map.py
│   └── utils.py
└── tests/
    ├── browser_test.py
    └── test_tools.py
```

## Notes

- The framework uses Ollama, not the Anthropic API.
- `app.py` is the Streamlit entry point.
- `src/cli.py` is the terminal entry point.
