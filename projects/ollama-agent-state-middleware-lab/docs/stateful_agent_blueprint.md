## Lab 13 Key Takeaways (Reusable Agent Build Pattern)

This lab establishes the preferred modern pattern for building stateful LangGraph agents.

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

### 10. Prefer framework-native patterns

Future prompt instruction:

> Build using latest LangGraph best practices. Use AgentState, ToolRuntime, Command(update), ToolMessage, MemorySaver, thread-based persistence, and clean separation between tools/state/orchestration. Avoid ad-hoc globals or custom hacks unless compatibility requires them.

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