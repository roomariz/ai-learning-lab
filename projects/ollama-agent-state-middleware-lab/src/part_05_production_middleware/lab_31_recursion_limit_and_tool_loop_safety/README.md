# 31 Tool Loop Safety

Purpose: Protect production agents from runaway tool-calling loops.

## Core lesson

Models do not always stop correctly.
Production agents need execution safety limits.

Runaway loops directly impact:

- cost
- latency
- stability
- resource exhaustion

## Demo

This lab shows:

- normal agent → runaway loop risk
- protected agent → safe stop

The protected agent uses:

- a total tool-call limit (`ToolCallLimitMiddleware`)
- a per-tool loop guard (`ToolLoopGuardMiddleware`)

Note: this lab does not use LangGraph's `recursion_limit` config directly.  
It teaches application-level tool-call safety through middleware.  
LangGraph recursion limits can still be added later as an additional runtime safety guard.

## Files

| File | Purpose |
|---|---|
| `app.py` | Runs normal vs protected agent demo |
| `middleware.py` | `ToolCallLimitMiddleware` implementation |
| `tools.py` | A looping tool that encourages repeated calls |
| `expected_output.md` | Example output |

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_31_recursion_limit_and_tool_loop_safety.app
```
