# 11 Context vs State

## Goal

Show the difference between runtime context and agent state.

## Simple distinction

Context is stable metadata supplied outside `AgentState`.

State is changing information tracked inside `AgentState`.

## Examples

Context:

1. User ID
2. Role
3. Tenant ID
4. Environment

State:

1. Current topic
2. Completed topics
3. Notes
4. Last action
5. Tool call count
6. Authorised tools

## Why this matters

Tools need both context and state, but for different reasons.

A tool may read context to know who is using the system.

A tool may read or write state to track what happened during the workflow.

Keeping these separate avoids confusion.

## Files in this lab

```txt
src/part_02_tools_and_runtime/lab_11_context_vs_state/
├── README.md
└── main.py
```

## Run

```bash
uv run python -m src.part_02_tools_and_runtime.lab_11_context_vs_state.main
```

## Expected behaviour

The exact assistant/tool-routing behaviour may vary because the agent uses the configured model.

The important behaviour is verified through the printed context and state after each step.

## Learning point

Do not mix context and state.

Context answers: who is using this run, under what role, and in what environment?

State answers: what has happened so far, what is the agent doing now, and what should happen next?