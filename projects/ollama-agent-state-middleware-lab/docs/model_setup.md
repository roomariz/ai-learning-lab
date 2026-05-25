# Model Setup (Ollama)

This lab is **local-first** and uses Ollama as the default model provider. OpenRouter is optional via environment variables.

## Recommended Ollama Models

This lab is designed to work best with a small local model set:

| Model | Purpose |
|---|---|
| `qwen3:14b` | Main agent model for LangChain agents, tool calling, reasoning, and middleware labs |
| `qwen2.5-coder:7b` | Coding-focused model for debugging, refactoring, and code generation |
| `nomic-embed-text` | Embedding model for retrieval and RAG workflows |

Note: `qwen3:14b` gives better tool-calling behaviour, but it is slower and needs more memory. If your machine struggles, use a smaller tool-capable model that you have pulled locally.

## Install Models

```bash
ollama pull qwen3:14b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

Verify the models are available:

```bash
ollama list
```

## Configure `.env`

Copy the example file and adjust models as needed:

```bash
cp .env.example .env
```

Key environment variables:

- `MODEL_PROVIDER=ollama`
- `OLLAMA_MODEL` (default main agent model)
- `OLLAMA_CODER_MODEL` (recommended coding-heavy alternative)
- `OLLAMA_EMBED_MODEL` (recommended embedding model for retrieval/RAG exercises)

Note: today, most labs use a single chat model (`OLLAMA_MODEL`). The extra model variables are included to make it easy to standardize your local setup across agent + coding + retrieval workflows.

