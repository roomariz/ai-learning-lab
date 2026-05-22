# 14 Middleware Concept

## Teaching goal

Middleware is code that runs around the agent.
It can observe, modify, block, or wrap execution without putting that logic inside every tool.

## What you will learn

Middleware wraps work with code that runs before and after the main action.

## What is inside

```txt
src/part_04_middleware/lab_14_middleware_concept/
├── README.md
├── main.py
└── expected_output.txt
```

## How to run

```bash
uv run python -m src.part_04_middleware.lab_14_middleware_concept.main
```

## Expected behaviour

The lab is deterministic. No model is called.

1. The first call runs without middleware.
2. The second call runs with middleware.
3. The middleware prints one line before the action.
4. The middleware prints one line after the action.
5. The middleware does not block, modify, authorise, or handle errors. It only observes.

## Why this order matters

The next labs build on this foundation:

| Lab | What it adds |
|-----|-------------|
| 14  | Middleware concept: before / after observation |
| 15  | Hooks: `before_tool` / `after_tool` |
| 16  | Input validation middleware |
| 17  | Tool authorisation middleware |
| 18  | Error handling middleware |
| 19  | Built-in middleware |
| 20  | Middleware execution order |

## Learning point

Separating observation from action is the first step toward production-grade middleware.
Once you can see what the agent does, you can later decide what to allow, block, or change.
