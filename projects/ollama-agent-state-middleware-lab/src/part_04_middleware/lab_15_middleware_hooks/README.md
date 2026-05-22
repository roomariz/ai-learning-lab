# 15 Middleware Hooks

## Goal

Show the main places where middleware-style logic can run around an agent action.

## What changed from Lab 14

Lab 14 showed the basic idea:

```txt
before → action → after
```

This lab expands that idea into more specific hook points:

```txt
before_agent → before_tool → tool → after_tool → after_agent
```

## Hook phases

```python
def before_agent(user_message: str) -> None:
    ...

def before_tool(tool_name: str) -> None:
    ...

def after_tool(tool_name: str, result: str) -> None:
    ...

def after_agent(final_result: str) -> None:
    ...
```

## Why this matters

Different middleware concerns belong at different points in the lifecycle:

* `before_agent`: logging, input checks, request setup
* `before_tool`: tool authorisation, rate limits, tool logging
* `after_tool`: output checks, tool result logging
* `after_agent`: final logging, metrics, cleanup

This keeps cross-cutting concerns separate from the tool’s main job.

## Files in this lab

```txt
src/part_04_middleware/lab_15_middleware_hooks/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_04_middleware.lab_15_middleware_hooks.main
```

## Expected behaviour

This lab is deterministic. No model is called.

The important behaviour is:

1. `before_agent` runs first.
2. `before_tool` runs before the tool.
3. The tool runs and adds a note.
4. `after_tool` runs after the tool.
5. `after_agent` runs last.
6. The printed output shows the full execution order.

## Learning point

Hooks give middleware clear lifecycle points.

Once you know where middleware runs, later labs can use those hook points for validation, authorisation, error handling, logging, and message trimming.
