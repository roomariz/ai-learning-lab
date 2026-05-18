# 14 Middleware Concept

## Goal

Show the middleware concept using deterministic Python functions.

## What changed from Lab 12

Lab 12 placed production controls directly inside the request flow.

This lab moves those controls into middleware-style functions.

## What middleware does

Middleware runs before the tool.

In this lab, middleware handles:

1. Input validation.
2. Tool authorisation.
3. Audit tracing.

If middleware blocks a request, the tool does not run.

## Why this matters

Without middleware, every request handler or tool must remember to perform the same checks.

With middleware, common controls are centralised.

This makes the agent easier to maintain and safer to extend.

## Files in this lab

```txt
src/14_middleware_concept/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.14_middleware_concept.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

Valid requests pass through middleware and reach the tool.
Empty input is blocked before the tool runs.
Unauthorised tools are blocked before the tool runs.
Audit middleware records successful middleware passage.
Tool logic stays focused on the actual operation.

## Learning point

Middleware separates control logic from business/tool logic.

That separation is one of the foundations of production-ready agents.