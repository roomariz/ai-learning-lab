# 11 Context vs State

## Goal

Show the difference between runtime context and agent state.

## Simple distinction

Context is stable information supplied to a run.

State is changing information tracked during a run.

## Examples

Context:

1. User ID.
2. Role.
3. Tenant ID.
4. Environment.
5. Authorised tools.

State:

1. Current topic.
2. Completed topics.
3. Notes.
4. Last action.
5. Tool call count.

## Why this matters

Tools need both context and state, but for different reasons.

A tool may read context to know who is using the system.

A tool may read or write state to track what happened during the workflow.

Keeping these separate avoids confusion.

## Files in this lab

```txt
src/11_context_vs_state/
├── README.md
├── main.py
└── expected_output.txt
```

Run

```bash
uv run python -m src.11_context_vs_state.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- Context contains stable run information.
- State contains changing agent information.
- A context tool reads context.
- A state tool reads state.
- A write tool updates state but does not change context.
- Final context stays the same, while final state changes.

## Learning point

Do not mix context and state.

Context answers: who is using this run, under what role, and in what environment?

State answers: what has happened so far, what is the agent doing now, and what should happen next?