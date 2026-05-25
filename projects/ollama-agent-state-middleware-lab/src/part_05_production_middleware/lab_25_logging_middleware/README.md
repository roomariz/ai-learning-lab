# 25 Logging Middleware

**Purpose:** Add observability so we can see when the agent starts, when tools run, and when the agent finishes.

**Key lesson:** Middleware can observe the agent lifecycle without changing the tool code.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Demo agent run with logging enabled |
| `middleware.py` | Middleware that logs agent lifecycle + tool calls |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_25_logging_middleware.app
```

