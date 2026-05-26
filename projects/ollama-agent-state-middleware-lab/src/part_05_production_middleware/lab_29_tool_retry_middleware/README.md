# 29 Tool Retry Middleware

Purpose: Retry temporary tool failures before returning a safe error.

## Core lesson

Production tools can fail temporarily.
A retry middleware can recover from transient failures without changing tool code.

Retry middleware is for transient failures only. It should not retry policy blocks, validation errors, or authorisation failures.

## Demo idea

The `flaky_tool` fails twice, then succeeds on the third attempt.

## Files

| File | Purpose |
|---|---|
| `app.py` | Runs the demo agent with retry enabled |
| `middleware.py` | `ToolRetryMiddleware` implementation |
| `tools.py` | A flaky tool that succeeds on attempt 3 |
| `expected_output.md` | Example output |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_29_tool_retry_middleware.app
```

