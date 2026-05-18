# 10 Writing State from Tools

## Goal

Show how tools can write to state in controlled ways.

## What changed from Lab 09

Lab 09 used read-only tools.

Those tools inspected state but did not change it.

This lab introduces write tools that deliberately mutate state through a runtime object.

## What the tools do

This lab has four tool actions:

1. Add a learning note.
2. Complete the current topic.
3. Set the next topic.
4. Attempt an unauthorised destructive write.

The destructive write is blocked.

## Why this matters

Writing state is powerful, but it must be controlled.

A production agent should not let every tool mutate state freely.

Instead, write operations should be explicit and predictable.

For example:

```python
runtime.add_note(note)
runtime.complete_topic(topic, next_topic)
runtime.record_tool_call(action)
```

## Files in this lab

```
src/10_writing_state_from_tools/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.10_writing_state_from_tools.main
```

## Expected behaviour

This lab does not call the model. It is deterministic.

The important behaviour is:

- The first tool adds a note.
- The second tool marks writing_state_from_tools as completed.
- The current topic moves to context_vs_state.
- The blocked admin write does not delete notes.
- The final state shows controlled mutation.

## Learning point

Reading state helps tools decide.

Writing state changes the agent's future behaviour.

That means write tools need stronger control than read-only tools.
