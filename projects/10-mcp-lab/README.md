# MCP Lab

This lab wires a LangChain agent to a simple MCP math server.

## Run

Start the MCP server:

```bash
uv run python main.py
```

Then run the client:

```bash
uv run python client_langchain.py
```

Agent execution is capped at 6 iterations to prevent infinite tool-calling loops.

## Ollama model selection

`client_langchain.py` reads the model name from `OLLAMA_MODEL` when set.
If unset, it queries the local Ollama server at `OLLAMA_HOST` and selects a model from
a built-in priority list (qwen2.5:7b, qwen2.5:3b, llama3.1:8b, llama3.2:3b, phi3:mini).
If none are installed, it falls back to the first available Ollama model.

Examples:

```bash
$env:OLLAMA_MODEL = "llama3.1:8b"
uv run python client_langchain.py
```

If Ollama is listening on a non-default host, set `OLLAMA_HOST` too:

```bash
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "qwen2.5:7b"
uv run python client_langchain.py
```
