# 07 Tool State Challenge

## Goal

Show why manually passing state into every tool becomes awkward.

## What changed from Lab 06

Lab 06 showed that tools can read and write state.

This lab shows the problem with that pattern.

Each tool must now manually handle:

1. Receiving state.
2. Checking authorisation.
3. Updating the tool call count.
4. Updating `last_action`.
5. Avoiding inconsistent mutation.

## Why this matters

Manual state passing is fine for a small example.

It becomes fragile when a project has many tools.

A missed check or forgotten update can create bugs.

For example, one tool may update `last_action`, another may forget. One tool may check authorisation, another may not.

## Files in this lab

```txt
src/07_tool_state_challenge/
├── README.md
├── main.py
└── expected_output.txt
Run
uv run python -m src.07_tool_state_challenge.main
Expected behaviour

This lab does not call the model. It is deterministic.

The important behaviour is:

The read tool is authorised and reads state.
The write tool is authorised and adds a note.
The complete-topic tool is not authorised and is blocked.
The final state shows that the blocked tool did not complete the topic.
The summary explains why this manual pattern becomes fragile.
Learning point

Tool state access is useful.

Manual state passing is the challenge.

The next lab introduces a cleaner runtime-style approach for tool state access.