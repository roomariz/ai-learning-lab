# MCP CLI Project

This project is a command-line chat client that talks to a local LLM through the wrapper in `core/ollama_client.py` and enriches responses with MCP tools, prompts, and document resources.

The default setup starts one document MCP server from `mcp_server.py` and can optionally attach additional MCP server scripts passed to `main.py`.

## What’s Included

- `main.py` - application entry point
- `mcp_server.py` - document MCP server with resources, tools, and a prompt
- `mcp_client.py` - async MCP client wrapper
- `core/chat.py` - base chat loop and tool execution flow
- `core/cli_chat.py` - CLI-specific document handling and prompt processing
- `core/cli.py` - prompt-toolkit UI, completions, and autosuggest
- `core/ollama_client.py` - local chat client wrapper for Ollama's `/api/chat`

## Requirements

- Python 3.10+
- `uv` recommended for dependency management
- A running Ollama server at `http://localhost:11434`

## Setup

### 1. Install dependencies

With `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Without `uv`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configure environment

Create a `.env` file in `projects/09-mcp-cli-project` if you want to override the default model:

```bash
OLLAMA_MODEL="llama3"
USE_UV="0"
```

- `OLLAMA_MODEL` selects the Ollama model used by `core/ollama_client.py`
- `USE_UV=1` makes `main.py` launch the MCP server with `uv run mcp_server.py`

## Running The App

Start the CLI:

```bash
uv run main.py
```

Or:

```bash
python main.py
```

You can also attach extra MCP server scripts:

```bash
uv run main.py path/to/extra_server.py
```

## How It Works

### Document context

The built-in MCP server exposes a document store through the `docs://documents` resource family.

- `docs://documents` returns the list of document IDs
- `docs://documents/{doc_id}` returns the contents of a document

The current sample documents are:

- `deposition.md`
- `report.pdf`
- `financials.docx`
- `outlook.pdf`
- `plan.md`
- `spec.txt`

### Tools

`mcp_server.py` currently exposes:

- `read_doc_contents`
- `edit_document`

### Prompt

The server also exposes a `format` prompt that rewrites a document in Markdown format.

### CLI behavior

The CLI in `core/cli.py` supports:

- `/` command completion for MCP prompts
- `@doc_id` document mentions for inline context injection
- `docs://documents` resource completion

The query flow in `core/cli_chat.py`:

1. Detects `/format doc_id` commands and fetches the corresponding MCP prompt
2. Detects `@document` mentions and injects document content into the chat context
3. Sends the final prompt to the chat model

## MCP Inspector

To inspect the document server directly:

```bash
uv run mcp dev mcp_server.py
```

This starts the MCP proxy and the MCP Inspector UI.

## Notes

- The code currently uses Ollama, not the Anthropic API.
- There are no lint or type-check commands defined in the project yet.
- `mcp_server.py` still contains a TODO for a summarize prompt.
