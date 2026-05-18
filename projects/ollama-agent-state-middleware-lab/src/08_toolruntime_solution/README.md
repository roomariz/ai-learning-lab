# 08 ToolRuntime Solution

## Goal

Show how a runtime-style object makes tool state access cleaner.

## What changed from Lab 07

Lab 07 showed the challenge:

1. Every tool received raw state.
2. Every tool had to check authorisation manually.
3. Every tool had to update shared bookkeeping manually.
4. The pattern became repetitive.

This lab introduces a small educational `ToolRuntime` class.

It groups:

1. `state`, which changes during the run.
2. `context`, which describes the run.
3. Helper methods for authorisation and bookkeeping.

## Why this matters

A runtime object gives tools one controlled interface.

Instead of passing many separate values into every tool, tools receive one object:

```python
def read_learning_status_tool(runtime: ToolRuntime) -> str:
    ...
```

This makes tool code easier to read, test, and extend.

> **Educational note**
>
> This lab uses a small custom ToolRuntime class to explain the concept.
>
> LangChain and LangGraph also provide runtime mechanisms for tools. Current LangChain documentation describes runtime context as dependency injection for tools and middleware, and the LangGraph reference documents ToolRuntime as an injected runtime parameter for tools.

## Files in this lab

```
src/08_toolruntime_solution/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.08_toolruntime_solution.main
```

## Expected behaviour

This lab does not call the model. It is deterministic.

The important behaviour is:

- The runtime object contains both state and context.
- A read tool reads state and context through runtime.
- A write tool adds a note through runtime.
- A progress tool completes `toolruntime_solution`.
- The current topic moves to `reading_state_in_tools`.
- Tool call count increases in one shared way.

## Learning point

Manual state passing works, but it becomes noisy.

A runtime object gives tools a cleaner and more controlled way to access state and context.