# 09 Reading State in Tools

## Goal

Show how tools can read `AgentState` through framework-injected `ToolRuntime` without changing domain state.

## What changed from Lab 08

Lab 08 showed `ToolRuntime` with both read and write tools.

This lab narrows the focus to read-only tools.

The tools can inspect:

1. Learner profile
2. Completed topics
3. Current topic
4. Authorised tool access

They return strings only. They do not return `Command(update={...})`.

## Why this matters

Not every tool should write to state.

Many tools only need to read state before deciding what to return.

Examples:

1. Read the user's role before showing a feature
2. Read the current workflow step before choosing the next instruction
3. Read completed tasks before recommending the next task
4. Read preferences before formatting an answer
5. Read permissions before allowing tool access

## Read-only convention

This lab uses real framework `ToolRuntime`:

```python
@tool
def read_profile(runtime: ToolRuntime) -> str:
    ...
```

The tools inspect `runtime.state`, but do not mutate domain state.

They return `str`, not `Command(update={...})`.

## Files in this lab

```
src/part_02_tools_and_runtime/lab_09_reading_state_in_tools/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_02_tools_and_runtime.lab_09_reading_state_in_tools.main
```

## Expected behaviour

This lab does call the model through the agent.

The tools:

- The profile tool reads learner name, preferred language, and role
- The progress tool reads completed topics and last action
- The next-topic tool reads the current topic
- The unauthorised read tool is blocked by `authorised_tools` in state
- No domain state fields are updated

## Learning point

Reading state lets tools make informed decisions without mutation.

The next lab (Lab 10) will focus on writing state from tools through `Command(update={...})`.