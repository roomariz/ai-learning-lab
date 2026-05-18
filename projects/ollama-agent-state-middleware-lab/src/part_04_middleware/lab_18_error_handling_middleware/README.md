# 18 Error Handling Middleware

## Goal

Show how error handling middleware catches and manages exceptions from tool execution.

## What changed from Lab 17

Lab 17 checked if a tool is allowed before it runs.

This lab handles what happens when a tool fails during execution.

## Error handling patterns

```python
class ErrorHandlingMiddleware:
    def handle_tool_error(self, tool_name, error) -> str:
        # Catches the exception, logs it, and returns a safe message.
        # Prevents the error from propagating.

    def handle_with_fallback(self, tool_name, error, fallback_value) -> str:
        # Catches the exception and returns a fallback value.
        # Used when partial failure is acceptable.

    def handle_with_retry(self, tool_name, error) -> str:
        # Catches the exception and records retry configuration.
        # The actual retry loop would run in the request handler.
```

## Why this matters

Tools fail. Networks time out, files are missing, data is malformed.

Without error handling middleware:

- A single tool failure crashes the agent loop.
- No recovery is possible.
- Errors propagate to the user as raw exceptions.

With error handling middleware:

- Errors are caught at the middleware layer.
- The agent can continue.
- Safe fallbacks or retries are possible.
- Error logs are useful for debugging.

## Files in this lab

```txt
src/18_error_handling_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.18_error_handling_middleware.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- `RuntimeError` from a tool is caught and reported safely.
- `KeyError` from a lookup tool is caught and reported.
- A fallback value is returned when a tool fails.
- Retry info is recorded from context.
- The error log tracks all errors with type and message.

## Learning point

Error handling middleware catches exceptions from tools. It can report errors safely, fall back to default values, or flag the error for retry. Without it, unhandled tool errors propagate up and break the agent loop.