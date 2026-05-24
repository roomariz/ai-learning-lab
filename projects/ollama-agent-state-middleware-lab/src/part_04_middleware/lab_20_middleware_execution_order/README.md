# 20 Middleware Execution Order

## Goal

Show that middleware ordering changes system behaviour.

## What changed from Lab 19

Lab 19 introduced framework-style hook names (before_model, after_model, wrap_tool_call).

This lab introduces four named middleware with distinct responsibilities:

- **ValidationMiddleware**: validates input before tool execution
- **AuthorisationMiddleware**: blocks dangerous tools
- **ErrorHandlingMiddleware**: catches tool errors gracefully
- **LoggingMiddleware**: wraps the full request lifecycle

Each middleware prints when it runs, so the execution order is visible in the output.

## Core concept: order matters

Same middleware, different order, different outcome.

Order A (correct):

```
validation
-> authorisation
-> tool
```

Order B (still works):

```
authorisation
-> validation
-> tool
```

Order C (broken):

```
tool
-> validation
```

In production:

- **validation** must happen before tool execution
- **authorisation** must happen before dangerous tools
- **error handling** must wrap risky execution
- **logging** may run around everything

## Execution model

Middleware is registered as a stack. `before` hooks run in registration order.
`after` and `error` hooks run in reverse order.

```
Registration order: [Logging, ErrorHandling, Validation, Authorisation]

Execution order:
  Logging.before          <- outermost
    ErrorHandling.before
      Validation.before
        Authorisation.before
          [tool]
  Logging.after           <- outermost
```

If any middleware blocks (returns False), the pipeline short-circuits but
outer middleware still runs its after hooks.

## Scenario outputs

### Normal flow

```
[logging] before
[validation] passed
[authorisation] passed
[tool] running add_note
[logging] after
```

### Validation blocks (empty input)

```
[logging] before
[validation] blocked
[logging] after
```

### Authorisation blocks (dangerous tool)

```
[logging] before
[validation] passed
[authorisation] blocked
[logging] after
```

### Tool crashes, error handler catches

```
[logging] before
[validation] passed
[authorisation] passed
[tool] running risky_note
[error handler] caught ValueError
[logging] after
```

## Files in this lab

```
src/part_04_middleware/lab_20_middleware_execution_order/
- README.md
- main.py
- expected_output.txt
```

## Run

```bash
uv run python -m src.part_04_middleware.lab_20_middleware_execution_order.main
```

Or via taskipy:

```bash
uv run task lab20
```

## Expected behaviour

This lab is deterministic. No model is called.

1. Four middleware run in a configurable pipeline.
2. Each middleware's `before` hook fires in registration order.
3. If a middleware blocks, the pipeline short-circuits.
4. `after` hooks fire in reverse registration order for middlewares
   that ran.
5. `error` hooks fire when a tool raises an exception.
6. Logging wraps everything. It is the outermost middleware.

## Learning point

Middleware is not just "what runs". It is "what runs first".

Order determines whether a system is secure, debuggable, and resilient, or broken.

This closes the middleware series. Earlier labs built the concept from
scratch. This lab shows how all pieces compose into a real pipeline.
