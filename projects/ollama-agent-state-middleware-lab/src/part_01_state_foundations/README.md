# Part 01: State Foundations

This section introduces the core concepts behind stateful AI agents.

The labs progress from isolated model calls toward structured and persisted agent state using LangChain and LangGraph-style patterns.

The focus of Part 01 is understanding:

- why message history alone is unreliable
- how structured agent state works
- how custom state schemas improve reliability
- why provider abstraction matters
- how checkpointer-based persistence works across invocations

Later sections build on these foundations with tools, runtime state access, middleware, and production workflows.

---

## Lab progression

### Lab 01 — Messages-Only Memory

```txt
lab_01_messages_only_memory
```

Demonstrates the limitation of isolated `model.invoke()` calls.

Key concept:
The model only sees messages passed into the current invocation.

Introduces:

- basic message structure
- `model.invoke()`
- system/human messages
- lack of persistence

---

### Lab 02 — Agent State Intro

```txt
lab_02_agent_state_intro
```

Introduces LangChain `AgentState`.

Key concept:
Agents can receive structured state alongside messages.

Introduces:

- `AgentState`
- `create_agent`
- `state_schema`
- structured invocation input

---

### Lab 03 — Custom State

```txt
lab_03_custom_state
```

Expands from one state field into richer structured state.

Key concept:
Production agents need multiple structured fields, not loose message history.

Introduces:

- custom `AgentState` schemas
- workflow/profile state
- structured learning progress
- state composition

---

### Lab 04 — Model Provider Setup

```txt
lab_04_model_provider_setup
```

Moves model/provider configuration into shared infrastructure.

Key concept:
Labs should not hard-code providers.

Introduces:

- provider abstraction
- shared config
- Ollama/OpenRouter switching
- local-first architecture

---

### Lab 05 — State Persistence

```txt
lab_05_state_persistence
```

Introduces persistence using `MemorySaver` and `thread_id`.

Key concept:
Structured state can persist across invocations.

Introduces:

- `MemorySaver`
- `thread_id`
- `agent.update_state`
- `agent.get_state`
- framework-native persistence

---

## Design principles in Part 01

### 1. One lab = one primary concept

Each lab teaches a focused idea without premature complexity.

### 2. Progressive architecture evolution

The sequence intentionally moves from:

```txt
model.invoke()
→ AgentState
→ custom state
→ provider abstraction
→ persistence
```

Later sections continue with:

```txt
ToolRuntime
→ Command(update)
→ ToolMessage
→ middleware
→ production workflows
```

### 3. Structured state over hidden memory

The repository treats structured state as the source of truth.

Important workflow data should not rely only on message history.

### 4. Framework-native patterns

Labs progressively align with modern LangChain/LangGraph patterns:

- `AgentState`
- `create_agent`
- `MemorySaver`
- `ToolRuntime`
- `Command(update={...})`
- `ToolMessage`

while keeping early labs intentionally simpler for learning clarity.