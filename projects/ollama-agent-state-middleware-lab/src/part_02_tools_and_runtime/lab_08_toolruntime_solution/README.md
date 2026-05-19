# 08 ToolRuntime Solution

## Goal

Show how framework-injected `ToolRuntime` gives tools clean access to agent state.

## What changed from Lab 07

Lab 07 showed the challenge:

1. Every tool received raw state.
2. Every tool had to check authorisation manually.
3. Every tool had to update shared bookkeeping manually.
4. The pattern became repetitive.

This lab uses the real LangChain `ToolRuntime` pattern.

`ToolRuntime` is injected by the framework when a tool is called. It is hidden from the LLM.

Tools access shared runtime information through `ToolRuntime`.

In this lab, tools primarily use:

1. `runtime.state` for persisted agent state
2. `runtime.tool_call_id` for `ToolMessage`

## Why this matters

A runtime object gives tools one controlled interface.

Instead of passing many separate values into every tool, tools receive one object:

```python
@tool
def read_learning_status(runtime: ToolRuntime) -> str:
    ...
```

This makes tool code easier to read, test, and extend.

## Files in this lab

```txt
src/part_02_tools_and_runtime/lab_08_toolruntime_solution/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_02_tools_and_runtime.lab_08_toolruntime_solution.main
```

## Expected behaviour

The exact assistant/tool-routing behaviour may vary because the agent uses the configured model.

The important behaviour is verified through the printed state after each step.

- The agent uses framework-injected `ToolRuntime`.
- Read tools access state through `runtime.state`.
- Write tools return `Command(update={...})`.
- `ToolMessage` records tool execution results.
- `MemorySaver` and `thread_id` persist state across invocations.
- Authorised tools are controlled through state.

## Learning point

`ToolRuntime` removes repetitive manual state passing.

Tools no longer need raw state arguments passed manually through the application.

The framework injects runtime automatically, giving tools controlled access to state, tool metadata, and persistent execution context.