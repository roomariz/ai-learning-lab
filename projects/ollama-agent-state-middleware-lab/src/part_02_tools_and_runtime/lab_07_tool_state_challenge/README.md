# 07 Tool State Challenge

## Goal

Show why manually passing state into every tool becomes awkward and fragile.

## What changed from Lab 06

Lab 06 showed the framework-native pattern using `ToolRuntime`, `Command(update={...})`, and `ToolMessage`.

This lab intentionally steps back to a manual pattern so the problem becomes clear.

Each tool must manually handle:

1. Receiving state
2. Checking authorisation
3. Updating the tool call count
4. Updating `last_action`
5. Avoiding inconsistent mutation

## Why this matters

Manual state passing is manageable in a small example.

It becomes fragile when a project has many tools.

A missed check or forgotten update can create bugs.

For example, one tool may update `last_action`, while another may forget. One tool may check authorisation, while another may bypass it.

## Bad pattern shown in this lab

```python
read_learning_status_tool(state)
add_learning_note_tool(state, note)
complete_topic_tool(state, topic)
```

Each tool receives and mutates the state manually.

## Files in this lab

```txt
src/part_02_tools_and_runtime/lab_07_tool_state_challenge/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_02_tools_and_runtime.lab_07_tool_state_challenge.main
```

## Expected behaviour

This lab does not call the model. It is deterministic.

The important behaviour is:

- The read tool is authorised and reads state.
- The write tool is authorised and adds a note.
- The complete-topic tool is not authorised and is blocked.
- The final state shows that the blocked tool did not complete the topic.
- The summary explains why this manual pattern becomes fragile.

## Learning point

Tool state access is useful.

Manual state passing is the challenge.

The next lab introduces a cleaner runtime-style approach for tool state access.