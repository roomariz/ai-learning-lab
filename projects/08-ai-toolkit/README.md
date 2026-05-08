# Tool-Calling Framework with Ollama

A Python framework for building LLM applications with tool-calling capabilities using Ollama. Enables an LLM to call various tools/functions based on user prompts, with support for tool chaining, async execution, retry logic, and structured logging.

## Features

- **Multiple Tools**: search_docs, read_document, summarise_document, extract_keywords, answer_question, get_chuck_norris_fact
- **Interactive CLI**: Enter prompts one at a time
- **Tool Validation**: JSON schema validation before execution
- **Structured Logging**: JSON-formatted logs with timestamps
- **Retry Logic**: Exponential backoff for failed API calls
- **Async Support**: Parallel tool execution
- **Tool Chaining**: Multi-step workflows

## Prerequisites

- **Python 3.8+**
- **Ollama** running locally (default: `http://localhost:11434`)
  - Install from [ollama.ai](https://ollama.ai)
  - Pull a model: `ollama pull llama3.1:latest`

## Installation

### Using uv (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tool
   ```

2. **Create and sync dependencies**
   ```bash
   uv venv && uv sync
   ```

3. **Install dev dependencies** (optional, for testing)
   ```bash
   uv pip install pytest
   ```

### Using pip

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tool
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate and install**
   ```bash
   # Linux/macOS
   source venv/bin/activate
   # Windows
   .\venv\Scripts\Activate.ps1

   pip install ollama rich jsonschema requests pytest streamlit
   ```

4. **Start Ollama service**
   ```bash
   # Ensure Ollama is running
   ollama serve
   # In another terminal, pull a model
   ollama pull llama3.1:latest
   ```

## Configuration

Configure via environment variables or edit `src/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `llama3.1:latest` | Model name |

Or edit `src/config.py` for additional settings:
- `max_iterations` - Maximum tool call iterations (default: 5)
- `timeout` - Request timeout in seconds (default: 30)
- `retry_attempts` - Number of retry attempts (default: 3)
- `retry_delay` - Delay between retries (default: 1.0s)

## Usage

### Step 1: Choose how to run the tool

| Method | Command | Description |
|--------|---------|-------------|
| **CLI** | `python src/cli.py` | Interactive command-line interface |
| **Streamlit UI** | `streamlit run app.py` | Web-based UI with tool explorer |
| **Batch Test** | `python src/run_tools.py` | Run test prompts automatically |
| **Unit Tests** | `pytest tests/ -v` | Run pytest test suite |

### Step 2: Web UI (Streamlit) Guide

To test using the web interface:

1. **Start the Streamlit server:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the URL shown (typically `http://localhost:8501`)

3. **Two modes available:**
   - **Interactive Mode**: Type a prompt and click "Run"
   - **Tool Explorer**: Browse and run individual tools manually

4. **Example web prompts:**
   - `Search docs for Python`
   - `Tell me a Chuck Norris fact`
   - `Extract keywords from machine learning`

### Step 3: Enter your prompt

The CLI/UI will detect which tool to use based on your prompt and execute it automatically.

### Interactive Mode

```
+------------------+
| Tool-Calling CLI |
+------------------+
Enter a prompt to process. Press Enter on empty line to exit.

> Hello, how are you?
```

### Example Prompts

| Prompt | Tool Used | Required Parameters |
|--------|-----------|---------------------|
| `Hello, how are you?` | None | - |
| `Search docs for Python.` | `search_docs` | `query` |
| `Read document 123.` | `read_document` | `doc_id` |
| `Summarise document 456.` | `summarise_document` | `doc_id` |
| `Extract keywords from this text.` | `extract_keywords` | `text` |
| `Answer: What is Python? Context: Python is a programming language.` | `answer_question` | `question`, `context` |
| `Tell me a Chuck Norris fact.` | `get_chuck_norris_fact` | - |

## Sample Data

Some tools return mock/sample data (except `get_chuck_norris_fact` which calls a real API):

| Tool | Sample Input | Sample Output |
|------|-------------|--------------|
| `search_docs` | `query="Python"` | List of doc titles, summaries, URLs |
| `read_document` | `doc_id="123"` | Document content with metadata |
| `summarise_document` | `doc_id="456"` | Document summary with word count |
| `extract_keywords` | `text="AI topics"` | Array of extracted keywords |
| `answer_question` | `question="What is AI?"` | Answer with confidence score |
| `get_chuck_norris_fact` | (none) | Random Chuck Norris joke from API |

## Project Structure

```
tool/
├── app.py              # Streamlit web UI
├── test_all_tools.py  # Integration test script
├── pyproject.toml      # Project configuration
│
├── src/
│   ├── cli.py          # Interactive CLI entry point
│   ├── run_tools.py    # Batch test runner
│   ├── functions.py    # Tool implementations (6 tools)
│   ├── tools_map.py    # Tool dispatcher mapping
│   ├── config.py       # Configuration settings
│   ├── utils.py        # Utility functions (retry, validation)
│   ├── logger.py       # Structured JSON logging
│   ├── chain.py        # Tool chaining (multi-step workflows)
│   └── async_runner.py # Async/parallel tool execution
│
└── tests/
    └── test_tools.py   # Unit tests
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `ollama` | >=0.4.0 | LLM integration |
| `rich` | latest | Terminal UI/formatting |
| `jsonschema` | latest | JSON schema validation |
| `requests` | latest | HTTP requests |
| `streamlit` | latest | Web UI framework |
| `pytest` | latest | Testing framework |
