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

## Ollama model selection

`client_langchain.py` now reads the model name from `OLLAMA_MODEL` when it is set.
If that variable is unset, it queries the local Ollama server at `OLLAMA_HOST`
and picks the first installed model it recognizes.

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
