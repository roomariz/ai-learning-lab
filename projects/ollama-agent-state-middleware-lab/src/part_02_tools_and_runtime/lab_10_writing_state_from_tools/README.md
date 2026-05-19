# 10 Writing State from Tools

## Goal

Show how tools can write to `AgentState` in controlled ways using `Command(update={...})`.

## What changed from Lab 09

Lab 09 used read-only tools.

Those tools inspected `runtime.state` and returned strings.

This lab introduces write tools that return `Command(update={...})` so the framework can apply explicit state updates.

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

Instead, write operations should return explicit updates:

```python
return Command(
    update={
        "notes": updated_notes,
        "last_action": "tool_added_learning_note",
        "messages": [
            ToolMessage(
                content="Note added",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    }
)
```

## Files in this lab

```
src/part_02_tools_and_runtime/lab_10_writing_state_from_tools/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_02_tools_and_runtime.lab_10_writing_state_from_tools.main
```

## Expected behaviour

The exact assistant/tool-routing behaviour may vary because the agent uses the configured model.

The important behaviour is verified through the printed state after each step.

- The first tool adds a note.
- The second tool marks `writing_state_from_tools` as completed.
- The current topic moves to `context_vs_state`.
- The blocked admin write does not delete notes.
- The final state shows controlled mutation through `Command(update={...})`.

## Learning point

Reading state helps tools decide.

Writing state changes the agent's future behaviour.

That means write tools need stronger control than read-only tools.