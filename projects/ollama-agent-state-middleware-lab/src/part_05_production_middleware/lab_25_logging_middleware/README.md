# 25 Logging Middleware

Purpose: Add observability so we can see what the agent is doing internally.

## Key lesson

Middleware can observe the agent lifecycle without modifying the agent or tool code.

This lab shows:

- when the agent starts
- when the model is called
- when a tool starts
- when a tool finishes
- when the model is called again after tool execution
- when the agent finishes

Important behaviour:

```text
model → tool → model
```

The first model call decides whether a tool is needed.
After the tool runs, the model is called again to generate the final response.

## Files

| File            | Purpose                                             |
| --------------- | --------------------------------------------------- |
| `app.py`        | Demonstrates agent execution with lifecycle logging |
| `middleware.py` | Logs agent lifecycle events and tool execution      |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_25_logging_middleware.app
```