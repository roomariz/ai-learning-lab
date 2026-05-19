# 12 Production-Ready Agents

## Goal

Show what changes when an agent moves from a learning demo towards production behaviour using framework-native patterns.

## Core idea

A production-ready agent should not rely on the model alone.

The application should add deterministic controls around the agent using framework-native LangGraph patterns.

## Lab Sequence

- Lab 09 = read state
- Lab 10 = write state
- Lab 11 = context vs state
- **Lab 12 = production controls around framework-native agents**

## Framework-Native Patterns Used

This lab uses LangGraph's native patterns:

1. **AgentState** - Structured state with type annotations
2. **create_agent** - Framework-native agent creation
3. **@tool** - Tool registration decorator
4. **ToolRuntime** - Framework-injected runtime for state access
5. **Command(update={...})** - Atomic state updates from tools
6. **ToolMessage** - Tool result communication
7. **MemorySaver + thread_id** - State persistence
8. **RunnableConfig** - Invocation configuration

## Production Controls Added

1. **Input validation before agent invocation** - Deterministic, not prompt-only
2. **Tool authorisation inside tools** - Runtime check via `is_tool_authorised`
3. **Safe blocking of unauthorised tools** - Updates state through `Command(update={...})`
4. **Controlled state updates** - Explicit updates via `Command(update={...})`
5. **Observability through counters** - `tool_call_count`, `blocked_request_count`, `error_count`

## Why This Matters

Models can produce useful language, but production systems need predictable controls.

This lab marks the transition from runtime fundamentals into production-oriented agent architecture.

Earlier labs focused on understanding tools, runtime access, and state management.

This lab introduces deterministic operational controls around framework-native agents.

1. Empty input should be blocked before the model sees it.
2. Unauthorised tools should not run.
3. Destructive or risky tools should be controlled.
4. State changes should be explicit and observable.
5. Counters and actions should make behaviour auditable.

## Files in This Lab

```txt
src/part_03_langgraph_capstone/lab_12_production_ready_agents/
├── README.md
├── main.py
└── expected_output.txt
```

## Run

```bash
uv run python -m src.part_03_langgraph_capstone.lab_12_production_ready_agents.main
```

## Expected Behaviour

This lab demonstrates deterministic production controls:

- **Step 1**: Valid request adds a learning note via agent
- **Step 2**: Empty input is blocked BEFORE agent invocation
- **Step 3**: Unauthorised risky tool is blocked by tool-level authorisation
- **Step 4**: Authorised completion tool updates progress via agent

The final state shows: `tool_call_count`, `blocked_request_count`, `error_count`, and `last_action`.

## Learning Point

Production readiness comes from control around the agent, not from prompts alone.

This lab combines everything learned so far (read/write state, context vs state) with production controls, without introducing middleware yet.

Middleware (Lab 13+) will add cross-cutting concerns.