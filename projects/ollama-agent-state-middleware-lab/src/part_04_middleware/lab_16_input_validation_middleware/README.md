# 16 Input Validation Middleware

## Goal

Show how a dedicated input validation middleware checks messages before they reach tools.

## What changed from Lab 13

Lab 13 bundled validation inside a generic middleware function.

This lab isolates input validation into its own `ValidationMiddleware` class with focused checks:

1. Length (min and max).
2. Empty check.
3. Pattern matching (blocked and allowed).
4. Sanitisation (control characters, whitespace).

## Validation checks

```python
class ValidationMiddleware:
    def validate_length(self, message) -> str | None:
        # Rejects messages outside [min, max] length.

    def validate_patterns(self, message) -> str | None:
        # Blocks messages matching blocked_patterns.
        # Requires at least one allowed_pattern match.

    def validate_not_empty(self, message) -> str | None:
        # Rejects empty or whitespace-only messages.

    def validate_sanitised(self, message) -> str | None:
        # Rejects control characters.
        # Logs sanitisation (e.g. whitespace stripping).
```

## Why this matters

Input is the most common attack surface.

Validation middleware:

- Stops empty or malformed messages early.
- Enforces length constraints to prevent buffer issues.
- Blocks XSS patterns and injection attempts.
- Cleans input before it reaches business logic.

## Files in this lab

```txt
src/16_input_validation_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.16_input_validation_middleware.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- Empty input is blocked.
- Too-short input is blocked.
- Too-long input is blocked.
- XSS patterns are blocked.
- Valid input passes all checks.
- The validation log tracks every check.

## Learning point

Input validation middleware protects the system from bad or malicious input. Length limits, pattern blocks, and sanitisation checks prevent common attacks and errors before they reach the tool layer.