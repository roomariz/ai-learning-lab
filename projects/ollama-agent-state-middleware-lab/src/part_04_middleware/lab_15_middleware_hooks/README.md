# 15 Middleware Hooks

## Goal

Show how middleware can implement hooks for lifecycle phases: before_request, after_request, and on_error.

## What changed from Lab 13

Lab 13 had flat middleware functions that return early on block.

This lab introduces a `MiddlewareWithHooks` class that tracks `before_request` and `after_request` calls around every request, regardless of whether it passes or is blocked.

## Hook phases

```python
class MiddlewareWithHooks:
    def before_request(self, runtime, request) -> None:
        """Called before checks run."""

    def check(self, runtime, request) -> str | None:
        """Validation or authorisation logic."""

    def after_request(self, runtime, request, result) -> None:
        """Called after the request is handled."""

    def on_error(self, runtime, request, error) -> None:
        """Called when an exception propagates."""
```

## Why this matters

Hooks separate lifecycle concerns:

- `before_request`: logging, metrics, request ID.
- `check`: validation, authorisation.
- `after_request`: response logging, audit trails.
- `on_error`: error recovery, alerting.

This avoids mixing cross-cutting concerns into business logic.

## Files in this lab

```txt
src/15_middleware_hooks/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.15_middleware_hooks.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- All three middleware instances log `before_request` on every request.
- All three log `after_request` after every request (blocked or passed).
- The `hook_log` tracks the full sequence.
- Tool calls and blocked counts are recorded.

## Learning point

Hooks give middleware a lifecycle. This makes it easier to add logging, metrics, or cleanup without mixing it into business logic.