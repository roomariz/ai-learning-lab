# 02 Agent State Intro

## Goal

Show how a LangChain agent can receive structured state alongside messages.

## Problem in Lab 01

The assistant could not remember the user's preferred programming language because the second call did not include the first message.

## What changes in this lab

This lab introduces a custom LangChain `AgentState` schema:

```python
from langchain.agents import AgentState

class PreferenceState(AgentState):
    preferred_language: str | None
```

The agent is created with `state_schema=PreferenceState`, which tells the agent to expect this custom field alongside the standard `messages` field.

## Key takeaway

Unlike a plain model call, an agent with a state schema can receive structured fields (like `preferred_language`) alongside messages in a single invocation. This is the foundation for tools that need to read/write state, and for persistence (covered in later labs with checkpointer and thread ID).