# 02 Agent State Intro

## Goal

Show how structured agent state solves the weakness demonstrated in Lab 01.

## Problem in Lab 01

The assistant could not remember the user's preferred programming language because the second call did not include the first message.

## What changes in this lab

This lab introduces a small `AgentState` object:

```python
class AgentState(TypedDict):
    preferred_language: str | None