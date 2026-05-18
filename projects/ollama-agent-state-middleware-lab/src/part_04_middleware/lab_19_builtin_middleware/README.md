# 19 Built-in Middleware

## Goal

Show LangGraph's built-in middleware hooks (`before_model` and `after_model`) and how they integrate into the agent lifecycle.

## What changed from Lab 18

Lab 18 built custom error handling middleware from scratch.

This lab uses LangGraph's built-in `create_middleware` to register hooks at the model level.

## Built-in middleware hooks

```python
from langchain.agents.middleware import create_middleware

middleware = create_middleware(
    name="my_middleware",
    before_model=lambda state, runtime: print("Before model call"),
    after_model=lambda state, runtime: print("After model call"),
)
```

## Hook phases

| Hook | When it runs |
|------|-------------|
| `before_model` | Before the LLM call |
| `after_model` | After the LLM call |

## Why this matters

LangGraph's built-in middleware gives you a standard way to inject logic around model calls:

- **Request ID**: tag each call with a unique ID for tracing.
- **Timing**: measure how long each model call takes.
- **Logging**: log inputs and outputs for audit.
- **Metrics**: record latency, token count, or error rates.

## Files in this lab

```txt
src/19_builtin_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.19_builtin_middleware.main
```

> Note: This lab calls the model. Make sure Ollama is running or your `.env` is configured for OpenRouter.

## Expected behaviour

The lab demonstrates:

- How `before_model` and `after_model` hooks are registered.
- The execution order of multiple middleware instances.
- A live agent invocation that triggers the middleware pipeline.

## Learning point

LangGraph provides built-in middleware hooks that run around each model call. These allow you to inject cross-cutting logic like request ID generation, timing, logging, and metrics collection without modifying the agent or tool code.