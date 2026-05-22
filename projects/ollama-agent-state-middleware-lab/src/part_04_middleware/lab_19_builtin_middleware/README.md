# 19 Built-in Middleware

## Goal

Show how earlier manual middleware ideas map to framework-style hook names.

## What changed from Lab 18

Lab 18 showed error handling middleware around tool execution.

This lab introduces built-in-style middleware hook names:

- `before_model`
- `after_model`
- `wrap_tool_call`

The lab is still deterministic. It uses a tiny fake model so the hook order is easy to understand.

## Core flow

```txt
user message
→ before_model
→ fake model decision
→ after_model
→ if tool is needed: wrap_tool_call
→ tool runs
```

## Hook phases

| Hook             | What it represents                         |
| ---------------- | ------------------------------------------ |
| `before_model`   | Runs before the model receives the message |
| `after_model`    | Runs after the model returns a decision    |
| `wrap_tool_call` | Runs around tool execution                 |

## Why this matters

Earlier labs built middleware manually:

* Lab 14: before / after observation
* Lab 15: lifecycle hook points
* Lab 16: validation before action
* Lab 17: authorisation before tool execution
* Lab 18: error handling around tool execution

This lab shows how those ideas map to standard framework-style hook points.

## Files in this lab

```txt
src/part_04_middleware/lab_19_builtin_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_04_middleware.lab_19_builtin_middleware.main
```

## Expected behaviour

This lab is deterministic. No model is called.

1. `before_model` runs before the fake model decision.
2. `after_model` runs after the fake model decision.
3. `wrap_tool_call` runs only when the fake model decides a tool is needed.
4. Scenario 1 calls `add_note`.
5. Scenario 2 does not call a tool.

## Learning point

Manual middleware teaches the concept.

Framework-style hooks give named places for that logic:

* model-level hooks
* tool-level wrappers
* post-processing hooks

This prepares the project for real LangGraph middleware and execution-order rules in Lab 20.
