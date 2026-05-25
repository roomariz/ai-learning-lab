# 24 Message Trimming Middleware

Purpose: Keep long conversations manageable before they reach the model.

## Key lesson

Middleware can edit the agent state before the model sees it.

This demo uses `max_messages=3` to make trimming obvious.

This lab shows two cases:

- A final user request survives trimming, so the agent can answer.
- The real request is trimmed away, so the agent may return no useful response.

## Files

| File | Purpose |
|---|---|
| `app.py` | Demonstrates how trimming affects long message history |
| `middleware.py` | Keeps only the most recent messages before the model runs |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_24_message_trimming_middleware.app
```
