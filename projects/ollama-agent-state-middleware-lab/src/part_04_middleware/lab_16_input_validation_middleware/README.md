# 16 Input Validation Middleware

## Goal

Show how middleware can block bad input before the main action runs.

## What changed from Lab 15

Lab 15 showed hook points that observe actions. This lab adds a decision:
the middleware can **block** execution, not just observe.

```txt
user_message → validation middleware → if valid: run action
                                    → if invalid: block before action
```

## The validation middleware

```python
def validate_input(user_message: str) -> str | None:
    if not user_message.strip():
        return "Blocked: message is empty."

    blocked_keywords = ["ignore", "override", "admin"]
    for keyword in blocked_keywords:
        if keyword in user_message.lower():
            return f"Blocked: message contains restricted keyword '{keyword}'."

    return None  # None means "valid, proceed"
```

The middleware returns:
- `None` → valid, the action runs
- A string → blocked, the action never runs

## Files in this lab

```txt
src/part_04_middleware/lab_16_input_validation_middleware/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_04_middleware.lab_16_input_validation_middleware.main
```

## Expected behaviour

Deterministic. No model is called.

1. Empty message → blocked by middleware, action never runs.
2. Message with "override" → blocked by middleware, action never runs.
3. Valid message → middleware passes, action runs, note is added.

## Learning point

Middleware can block before work happens.

Validation is the simplest case: check the input, reject it early if it fails.
The core action never needs to think about input validation.
