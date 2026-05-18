# 12 Production-Ready Agents

## Goal

Show what changes when an agent moves from a learning demo towards production behaviour.

## Key idea

A production-ready agent should not rely on the model alone.

The application should add deterministic controls around the agent.

## What this lab demonstrates

This lab uses a simple runtime object and deterministic checks for:

1. Input validation.
2. Tool authorisation.
3. Safe blocking of unauthorised tools.
4. Controlled state updates.
5. Basic observability through counters and `last_action`.

## Why this matters

Models can produce useful language, but production systems need predictable controls.

For example:

1. Empty input should be blocked before the model sees it.
2. Unauthorised tools should not run.
3. Destructive or risky tools should be controlled.
4. State changes should be explicit.
5. Counters and actions should make behaviour auditable.

## Files in this lab

```txt
src/12_production_ready_agents/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.12_production_ready_agents.main
```

## Expected behaviour

This lab is deterministic and does not call the model.

The important behaviour is:

- A valid request adds a learning note.
- Empty input is blocked.
- An unauthorised risky tool is blocked.
- An authorised completion tool updates progress.
- The final state shows tool calls, blocked requests, and errors.

## Learning point

Production readiness comes from control around the agent, not from prompts alone.

Validation, authorisation, error handling, observability, and controlled state mutation are core production concerns.
