# 13 Bug Tracker Agent with LangGraph

## Goal

Introduce a bug tracking pattern using LangGraph-style state. The agent can create, list, resolve, and reopen bugs — all through state mutations.

## What changed from Lab 12

Lab 12 placed production controls directly inside the request flow.

This lab shifts from production controls into applied state-driven workflows.

## Lab overview

Lab 13 is an interactive bug tracker demo that teaches LangGraph state management using a local Ollama model.

It demonstrates:
- custom bug-tracking state extending `AgentState`
- runtime-based state reads via `ToolRuntime`
- `Command(update={...})` state updates
- bug lifecycle actions: list, create, resolve, reopen

## State shape

```python
class BugState(AgentState):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    bugs: list[dict]
    next_bug_id: int
```

Each bug is a dict with `id`, `title`, `severity`, and `resolved`.

## Tools

### list_bugs
Reads all bugs from state in ID order. Returns a formatted list.

### list_bugs_by_severity
Reads all bugs from state sorted by severity (high → medium → low), then by ID.

### create_bug
Appends a new bug to the `bugs` list and increments `next_bug_id`.

### resolve_bug
Marks a bug as resolved by updating its `resolved` field.

### reopen_bug
Reopens a resolved bug by setting `resolved` back to `False`.

## Why this matters

Bug tracking is a natural example of state mutation:

- Create adds structured data.
- Resolve updates workflow state.
- Reopen reverses a previous state transition.

LangGraph's `Command(update={...})` pattern makes these state transitions explicit, traceable, and persistent across conversation turns.

## Files in this lab

```txt
src/part_03_langgraph_capstone/lab_13_bug_tracker_agent_langgraph/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run task lab13
```

This starts the interactive bug tracker.

## Expected behaviour

This lab runs interactively and uses the configured local Ollama model.

The important behaviour is:

- Listing bugs on an empty state returns `No bugs reported.`
- Creating three bugs increments next_bug_id.
- Listing bugs by severity sorts them high → medium → low.
- Resolving a bug marks it resolved.
- Resolving an already-resolved bug returns a message.
- Reopening a bug flips resolved back to False.
- Final state shows all bugs with correct IDs and statuses.

## Learning point

State mutation through Command-based tools such as create, resolve, and reopen mirrors real engineering workflows. Bug tracking gives the agent a structured memory for tracking issues, not just conversation history.