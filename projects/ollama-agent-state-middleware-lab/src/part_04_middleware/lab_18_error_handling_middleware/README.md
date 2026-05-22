# 18 Error Handling Middleware

## Goal

Show how middleware can catch an error from the action and return a
controlled message instead of crashing.

## Progression

- Lab 16 = block bad input
- Lab 17 = block unauthorised tools
- Lab 18 = catch tool/action errors

## Core flow

```
request
-> middleware
-> action runs
-> if action succeeds: return result
-> if action fails: catch error and return controlled message
```

## Tools

| Tool        | Behaviour                    |
|-------------|------------------------------|
| `safe_note` | Adds the note, succeeds      |
| `risky_note`| Raises `ValueError`          |

## Files

```
src/part_04_middleware/lab_18_error_handling_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_04_middleware.lab_18_error_handling_middleware.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

- `safe_note` succeeds and the note is added.
- `risky_note` raises `ValueError`, which is caught by the middleware.
- The middleware returns a controlled error message instead of crashing.
- An unknown tool name returns an error message.
- Valid notes are preserved across calls.

## Learning point

Error handling middleware wraps tool execution in a try/except. When a tool
raises an exception, the middleware catches it and returns a controlled error
message instead of letting the exception propagate. This keeps the agent loop
running.
