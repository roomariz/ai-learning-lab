# 23 Error Handling Middleware

Purpose: Catch tool failures and return safe, learner-friendly error messages instead of crashing the agent.

## Key lesson

- Without error middleware: tool error → agent may crash.
- With error middleware: tool error → safe `ToolMessage` → agent can continue.

## Demo prompt

This lab forces a tool crash to prove the middleware works:

```text
Use broken_quiz_generator for Python decorators
```

## Files

| File | Purpose |
|------|---------|
| `app.py` | Agent setup + demo failing tool |
| `middleware.py` | Tool error handling middleware |
| `tools.py` | Broken tool that always fails |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_23_error_handling_middleware.app
```
