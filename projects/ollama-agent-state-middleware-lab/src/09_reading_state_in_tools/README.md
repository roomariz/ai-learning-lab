# 09 Reading State in Tools

## Goal

Show how tools can read state without changing it.

## What changed from Lab 08

Lab 08 introduced a runtime-style object containing both state and context.

This lab narrows the focus to read-only tools.

The tools can inspect:

1. Learner profile.
2. Completed topics.
3. Current topic.
4. Authorised tool access.

They do not update state.

## Why this matters

Not every tool should write to state.

Many tools only need to read state before deciding what to return.

Examples:

1. Read the user's role before showing a feature.
2. Read the current workflow step before choosing the next instruction.
3. Read completed tasks before recommending the next task.
4. Read preferences before formatting an answer.
5. Read permissions before allowing tool access.

## Read-only convention

This lab uses:

```python
@dataclass(frozen=True)
class ReadOnlyToolRuntime:
    state: ReadOnlyState
    context: ReadOnlyContext

This makes the runtime reference read-only, but the state is still a dictionary.

So this is an educational convention, not full immutability.

The important lesson is design intent: these tools should read state, not mutate it.

Files in this lab
src/09_reading_state_in_tools/
├── README.md
├── main.py
└── expected_output.txt
Run
uv run python -m src.09_reading_state_in_tools.main
Expected behaviour

This lab does not call the model. It is deterministic.

The important behaviour is:

The profile tool reads learner name, preferred language, and role.
The progress tool reads completed topics and last action.
The next-topic tool reads the current topic.
The unauthorised read tool is blocked.
Final state is unchanged.
Learning point

Reading state lets tools make informed decisions.

Read-only tools should avoid mutation.

The next lab will focus on writing state from tools.
