# 13 Bug Tracker Agent with LangGraph

## Goal

Introduce a bug tracking pattern using LangGraph state. The agent can create, list, resolve, and reopen bugs — all through state mutations.

## What changed from Lab 12

Lab 12 placed production controls directly inside the request flow.

This lab focuses on a different layer: how the agent tracks and manages persistent data using typed state and runtime-style tools.

## State shape

```python
class BugState(TypedDict):
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

### list_bugs_tool
Reads all bugs from state. Returns a formatted list.

### create_bug_tool
Appends a new bug to the `bugs` list and increments `next_bug_id`.

### resolve_bug_tool
Marks a bug as resolved by updating its `resolved` field.

### reopen_bug_tool
Reopens a resolved bug by setting `resolved` back to `False`.

## Why this matters

Bug tracking is a real engineering workflow. It naturally maps to state mutation:

- Create adds to a collection.
- Resolve marks a flag.
- Reopen flips the flag back.

LangGraph's `Command(update={...})` pattern makes these mutations explicit and traceable.

## Files in this lab

```txt
src/13_bug_tracker_agent_langgraph/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.13_bug_tracker_agent_langgraph.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- Listing bugs on an empty state returns an empty message.
- Creating three bugs increments next_bug_id.
- Resolving a bug marks it resolved.
- Resolving an already-resolved bug returns a message.
- Reopening a bug flips resolved back to False.
- Final state shows all bugs with correct IDs and statuses.

## Learning point

State mutation through tools like create, resolve, and reopen mirrors real engineering workflows. Bug tracking gives the agent a structured memory for tracking issues, not just conversation history.