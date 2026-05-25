# 22 Tool Authorisation Middleware

Purpose: Add the first production control: free users cannot access premium learning tools.

## Teaching point

- `invoke()` waits for the whole agent run, then returns the final state.
- `stream()` shows agent and tool updates as they happen.
- Middleware controls whether a tool may execute.
- The model can still respond, but blocked tools do not run.

## Files

| File | Purpose |
|---|---|
| `app.py` | Creates the agent and demonstrates `invoke()` and `stream()` |
| `middleware.py` | Blocks premium tools for free users |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_22_tool_authorisation_middleware.app
```