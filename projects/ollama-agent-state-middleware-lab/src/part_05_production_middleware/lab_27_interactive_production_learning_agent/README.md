# 27 Interactive Production Learning Agent

Purpose: Try the complete production learning agent in an interactive terminal chat.

## Key lesson

A production agent can be used as a normal chat interface while middleware runs quietly in the background.

This lab reuses the production middleware stack from Lab 26:

- logging
- message trimming
- tool authorisation
- error handling

It also uses a small recursion limit so local tool-calling loops stop safely instead of running forever.

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_27_interactive_production_learning_agent.app
```