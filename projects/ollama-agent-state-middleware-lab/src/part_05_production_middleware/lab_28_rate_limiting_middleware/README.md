# 28 Rate Limiting Middleware

Purpose: Limit how many tool calls an agent can make in one request.

## Core lesson

Production agents need resource limits. Even valid users should not be allowed unlimited tool calls.

## Demo idea

Set `max_tool_calls=1`.

User asks:

> Explain Python decorators and then create a study plan

Expected:

- First tool call allowed
- Second tool call blocked
- Agent asks the user to split the request into smaller steps

## Files

| File | Purpose |
|---|---|
| `app.py` | Runs a small demo prompt with a strict tool-call limit |
| `middleware.py` | `RateLimitingMiddleware` implementation |
| `expected_output.md` | Example output showing the block |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_28_rate_limiting_middleware.app
```