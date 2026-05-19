# Stateful Agent Blueprint

This document defines the preferred architecture standard for framework-based agents in this repository.

### 1. Use `AgentState` for structured persistent memory

Do not rely only on conversation history.

Define explicit typed state:

```python
class CustomState(AgentState):
    items: list[dict]
    next_id: int
    last_action: str
```

Why:

* deterministic state management
* explicit schema
* easier debugging
* predictable agent behaviour
* scalable for production workflows

Use this whenever the agent must remember entities, workflow progress, flags, counters, or structured data.

---

### 2. Read state via `ToolRuntime`

Pattern:

```python
runtime.state.get("items", [])
```

Why:

* tools access live agent state safely
* avoids hidden globals
* keeps tools stateless and reusable
* matches LangGraph design

Best practice:
All read operations should happen inside tools via `ToolRuntime`.

---

### 3. Mutate state via `Command(update={...})`

Pattern:

```python
return Command(
    update={
        "items": updated_items,
        "next_id": next_id + 1,
    }
)
```

Why:

* explicit state mutation
* auditable transitions
* deterministic updates
* framework-native approach

Never mutate state directly inside the agent.

---

### 4. Use `ToolMessage` for tool result propagation

Pattern:

```python
ToolMessage(
    content="Created item",
    tool_call_id=runtime.tool_call_id,
)
```

Why:
Without this, the LLM may paraphrase or ignore tool output.

Best for:

* exact confirmations
* deterministic outputs
* operational workflows

---

### 5. Persist state with `MemorySaver`

Pattern:

```python
checkpointer=MemorySaver()
```

Why:
Maintains state across turns using thread context.

Without it:
state resets every interaction.

Use when building:

* task managers
* ticket systems
* shopping carts
* workflow agents
* approval systems
* bug trackers

---

### 6. Use stable `thread_id`

Pattern:

```python
config = {
    "configurable": {
        "thread_id": "agent-demo"
    }
}
```

Why:
State persistence depends on consistent thread identity.

---

### 7. Print only new `ToolMessage`s

Important lesson.

Wrong:

```python
result["messages"]
```

Problem:
prints historical tool outputs repeatedly.

Correct:

```python
state_before = agent.get_state(config)
msg_count_before = len(state_before.values["messages"])
new_messages = messages[msg_count_before:]
```

Why:
prevents duplicate historical outputs.

---

### 8. Separate responsibilities

Architecture:

* Agent = reasoning/orchestration
* Tools = state read/write logic
* State = structured memory
* Checkpointer = persistence
* UI loop = interaction

Best practice:
Never mix all logic in one place.

---

### 9. Interactive mode for testing

Best testing pattern:

```python
while True:
    user_input = input("You: ")
```

Why:
lets you validate:

* create
* read
* update
* edge cases
* persistence
* tool behaviour

---

### 10. Prefer framework-native state and orchestration patterns

Future prompt instruction:

> Build using latest LangGraph best practices. Use AgentState, ToolRuntime, Command(update), ToolMessage, MemorySaver, thread-based persistence, and clean separation between tools/state/orchestration. Avoid ad-hoc globals or custom hacks unless compatibility requires them.

---

### 11. Use explicit typed domain models where possible

Current:

```python
items: list[dict]
```

Better for larger systems:

```python
from dataclasses import dataclass

@dataclass
class Bug:
    id: int
    title: str
    severity: str
    resolved: bool
```

Why:

* stronger typing
* safer refactoring
* clearer contracts
* easier validation
* cleaner tooling support

Use raw dicts only for small teaching labs.

---

### 12. Keep business logic inside tools, not prompts

Bad pattern:

```text
LLM decides business rules
```

Preferred:

```python
resolve_bug()
create_bug()
validate_input()
```

Why:

* deterministic behaviour
* auditable workflows
* safer production systems
* easier testing

Prompts should guide reasoning, not enforce critical rules.

---

### 13. Treat the LLM as orchestration, not source of truth

Best practice:

```text
LLM = planner/reasoner
State = source of truth
Tools = execution layer
```

Never trust the model to reliably remember:

* IDs
* permissions
* workflow status
* financial data
* approval state

Persist important data in structured state.

---

### 14. Prefer deterministic workflows for production actions

Examples:

* approvals
* ticket resolution
* payments
* provisioning
* compliance flows

Pattern:

```python
Tool -> validate -> mutate state -> return ToolMessage
```

Avoid:

* hidden prompt logic
* implicit state assumptions
* free-form mutation

---

### 15. Add middleware around sensitive workflows

Future production pattern:

```text
before_agent
before_model
wrap_tool_call
after_model
after_agent
```

Use middleware for:

* validation
* authorisation
* rate limits
* logging
* observability
* retries
* PII filtering

State management alone is not enough for production agents.

---

### 16. Production-ready agents require observability

Track:

* tool calls
* failures
* blocked actions
* retries
* latency
* token usage
* state transitions

Why:

Without observability, debugging agent workflows becomes extremely difficult.

---

### 17. Repository learning design principle

One lab should focus on one primary concept.

Examples:

- Lab 01 = isolated message calls
- Lab 03 = custom state
- Lab 05 = persistence
- Lab 06 = tool state access
- Lab 13 = full blueprint

This keeps learning incremental, avoids premature complexity, and makes debugging easier for learners.

---

### 18. Prefer progressive architecture evolution

Recommended sequence:

```text
1. model.invoke
2. create_agent
3. AgentState
4. ToolRuntime
5. Command(update)
6. ToolMessage
7. MemorySaver
8. Middleware
9. Full production workflows
```

This keeps learning incremental and avoids overengineering beginner labs.

---

### 19. Repository standard

Framework-based labs should follow:

* `AgentState`
* `ToolRuntime`
* `Command(update={...})`
* `ToolMessage`
* `MemorySaver`
* thread-based persistence
* interactive testing loop
* separation of orchestration/state/tools

Exceptions should only exist when the lab intentionally teaches a lower-level concept.

---

### 20. Avoid ad-hoc globals and hidden mutable state

Avoid:

```python
GLOBAL_BUGS = []
```

Prefer:

```python
runtime.state["bugs"]
```

Why:

* safer concurrency
* persistence support
* easier testing
* framework compatibility
* predictable behaviour

---

## Important production principle

The LLM should never be treated as durable memory, workflow authority, or the system of record.

Production systems should persist important state explicitly and enforce critical business rules deterministically through tools, middleware, validation, and structured state transitions.

---

## Reusable concept categories

Use this architecture for:

* Task manager
* CRM agent
* Bug tracker
* Approval workflow
* Support ticket agent
* Order tracking agent
* Interview tracker
* Research tracker
* Learning progress agent
* Multi-step workflow assistants

This is your reference “stateful agent blueprint.”