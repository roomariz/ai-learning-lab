# 20 Middleware Execution Order

## Goal

Show how middleware execution order works when multiple middleware instances are registered.

## What changed from Lab 19

Lab 19 introduced built-in middleware hooks (before_model, after_model).

This lab demonstrates that:

- `before_model` hooks run in registration order.
- `after_model` hooks run in **reverse** registration order.

This mirrors the "Russian doll" pattern common in web frameworks.

## Execution model

For middleware `[A, B, C]`:

```
Request enters:
  A before_model  <- first
  B before_model
  C before_model
  [model call]
  C after_model   <- first to run after model
  B after_model
  A after_model   <- last
Response exits
```

## Why this matters

Knowing the execution order matters when middleware has dependencies:

- Logging should run first (wraps everything).
- Auth should run last on the way in (gatekeeper).
- Metrics should run outermost (captures everything).

## Files in this lab

```txt
src/20_middleware_execution_order/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.20_middleware_execution_order.main
```

> Note: This lab calls the model. Make sure Ollama is running or your `.env` is configured for OpenRouter.

## Expected behaviour

The output shows:

- Middleware A's `before_model` runs before Middleware B's.
- Middleware B's `after_model` runs before Middleware A's.
- The execution order follows the Russian doll pattern.

## Learning point

Middleware execution order follows a predictable nesting pattern. `before_model` runs in registration order, and `after_model` runs in reverse. This allows middleware to wrap the model call cleanly.