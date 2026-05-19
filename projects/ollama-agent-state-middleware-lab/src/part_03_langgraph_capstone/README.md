# Part 03: LangGraph Capstones

This section moves from runtime fundamentals into applied LangGraph workflows.

Earlier sections focused on:
- tools
- runtime access
- state reads and writes
- context vs state separation
- deterministic production controls

Part 03 applies those concepts to larger, workflow-oriented agents that manage structured state across multiple interactions.

The focus is no longer just "how tools work", but how agents manage persistent workflow state in realistic engineering scenarios.

---

## Learning progression

| Lab | Focus                     | Key concept                                |
| --- | ------------------------- | ------------------------------------------ |
| 12  | Production-ready agents   | Deterministic controls around agents       |
| 13  | Bug tracker capstone      | Persistent workflow state and mutations    |

---

## Labs

### Lab 12 — Production-Ready Agents

**Goal:** Add deterministic operational controls around framework-native LangGraph agents.

**Run:**
```bash
uv run python -m src.part_03_langgraph_capstone.lab_12_production_ready_agents.main
```

**Learning focus:**
- Input validation
- Tool authorisation
- Observability
- Safe failure handling
- Deterministic controls
- Production-safe state updates

**Learning point:**

Production agents should not rely entirely on model behaviour.

Deterministic controls around the model improve:
- safety
- predictability
- debugging
- observability
- operational reliability

**Files:**
```
lab_12_production_ready_agents/
├── README.md
├── main.py
└── expected_output.txt
```

---

### Lab 13 — Bug Tracker Agent with LangGraph

**Goal:** Build a stateful workflow agent that manages a persistent bug-tracking system through LangGraph state mutation patterns.

**Run:**
```bash
uv run task lab13
```

**Learning focus:**
- Stateful workflow design
- Persistent structured state
- Runtime-driven state reads
- `Command(update={...})`
- Workflow state transitions
- Interactive stateful agents

**Learning point:**

Bug tracking is a natural example of persistent workflow state:
- create → adds structured data
- resolve → updates workflow state
- reopen → reverses a previous transition

This lab demonstrates how LangGraph agents maintain structured memory across conversation turns, not just message history.

**Files:**
```
lab_13_bug_tracker_agent_langgraph/
├── README.md
├── main.py
└── expected_output.txt
```

---

## Recommended learning order

Follow the labs sequentially:

```
12 → 13
```

Each lab builds on the runtime and state concepts introduced earlier in the course.

---

## Architectural progression

| Stage                | Concept                                     |
| -------------------- | ------------------------------------------- |
| Runtime fundamentals | Tools, runtime, reads, writes, state        |
| Production controls  | Validation, authorisation, observability    |
| Applied workflows    | Persistent domain-specific state management |

---

## Core concepts reinforced

| Concept                        | Reinforced in |
| ------------------------------ | ------------- |
| `AgentState`                   | Lab 12–13     |
| `ToolRuntime`                  | Lab 12–13     |
| `Command(update={...})`        | Lab 12–13     |
| `ToolMessage`                  | Lab 12–13     |
| `MemorySaver`                  | Lab 12–13     |
| Stateful workflow mutation     | Lab 13        |
| Deterministic production logic | Lab 12        |

---

## Important design principles

1. **Structured state scales better than message-only memory**
   Real workflows require explicit state fields and controlled updates.

2. **State mutations should be explicit**
   `Command(update={...})` makes workflow transitions predictable and traceable.

3. **Production agents need deterministic controls**
   Validation, authorisation, and observability should exist outside prompts.

4. **Workflow state is not conversation history**
   Persistent application state should model real system behaviour.

5. **Runtime access should remain framework-managed**
   `ToolRuntime` keeps tools clean, consistent, and state-aware.
