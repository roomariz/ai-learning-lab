# 26 Complete Production Learning Agent

Purpose: Combine multiple middleware layers into one production-style learning agent.

## Middleware stack

1. Message trimming middleware
2. Logging middleware
3. Tool authorisation middleware
4. Error handling middleware

## Key lesson

Middleware layers compose cleanly.

A production agent is not one large class.
It is multiple focused middleware layers working together.

This capstone demonstrates:

- normal tool execution
- premium tool blocking
- safe tool failure handling
- long-history message trimming
- lifecycle logging

## Run

```bash
uv run python -m src.part_05_production_middleware.lab_26_complete_production_learning_agent.app
```