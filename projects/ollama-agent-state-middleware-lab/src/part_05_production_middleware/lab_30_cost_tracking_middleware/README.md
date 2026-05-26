# 30 Cost Tracking Middleware

Purpose: Track rough usage and compute cost signals during agent execution.

## Core lesson

Production agents need cost visibility.

Even local models have cost:
- execution time
- memory / compute usage
- repeated model calls
- tool usage

Cost tracking helps operators understand how resource-heavy an agent run is

## Demo idea

Track a request that uses multiple tools.

Expected logs:

- request started
- message count before / after model calls
- tool call count
- elapsed execution time
- rough local compute load category

## Files

| File | Purpose |
|---|---|
| `app.py` | Runs a multi-tool demo request |
| `middleware.py` | `CostTrackingMiddleware` implementation |
| `expected_output.md` | Example cost logs |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_30_cost_tracking_middleware.app
```