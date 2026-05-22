# Stateful Agent Learning Blueprint

This document defines the preferred learning and architecture standard for framework-based agents in this repository.

It is not a complete production-hardening checklist.

The labs teach the core architecture:

* structured state
* framework-managed runtime access
* explicit state mutation
* thread-based persistence
* deterministic controls around model behaviour
* clean separation between orchestration, tools, state, and UI

Production systems should build on these patterns with additional hardening, listed near the end of this document.

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

---

### 1. Use explicit structured persistent state

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

### 2. Read tool state via `ToolRuntime`

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
Tool state reads should generally use `ToolRuntime`.

Deterministic application or orchestration logic may also inspect state where appropriate, for example when rendering UI, validating a request before agent invocation, producing summaries, or running tests.

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

Note:
`Command(update={...})` handles state mutation only. When a tool also needs to propagate a conversational output to the LLM, combine this with `ToolMessage` as described in the next section.

---

### 4. Propagate conversational tool output via `ToolMessage`

Use `ToolMessage` when the LLM must receive a tool's exact output without paraphrase or omission.

Pattern:

```python
return Command(
    update={
        "messages": [
            ToolMessage(
                content="Created item",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    }
)
```

When combined with state mutation:

```python
return Command(
    update={
        "items": updated_items,
        "next_id": next_id + 1,
        "messages": [
            ToolMessage(
                content="Created item",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    }
)
```

Why:
`ToolMessage` explicitly adds exact tool output to conversational state when deterministic propagation is required.

Separate concerns:
* `Command(update={...})` handles state mutation.
* `ToolMessage` in the `messages` list handles conversational output propagation.

Best for:

* exact confirmations
* deterministic outputs
* operational workflows

---

### 5. Use `InMemorySaver` for labs and local development

Pattern:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
```

Why:
Maintains state across turns using thread context.

Without a checkpointer:
state resets every interaction.

Use `InMemorySaver` for:

* demos
* labs
* local development
* small teaching examples

Do not treat `InMemorySaver` as the production default.

Production persistence should use a durable backend such as PostgreSQL-backed checkpointing, SQLite-backed persistence for smaller deployments, or another deployment-appropriate datastore.

Use durable persistence when building:

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

If the `thread_id` changes unexpectedly, the agent may appear to forget previous state because it is reading from a different persisted thread.

Production thread identifiers must be:

* stable
* uniquely scoped to user, tenant, session, or workflow context

Warning: Reusing `thread_id` values across different users or sessions causes state leakage. Each user, tenant, or independent workflow context requires its own unique thread identifier.

---

### 7. Separate responsibilities

Architecture:

* Agent = reasoning/orchestration
* Tools = execution and state interaction
* State = structured source of truth
* Middleware = validation, policy enforcement, logging, retries, guardrails
* Checkpointer = persistence
* UI loop = interaction

Best practice:
Never mix all logic in one place.

---

### 8. Use interactive mode for exploratory learning

Useful learning pattern:

```python
while True:
    user_input = input("You: ")
```

Why:
lets you manually validate:

* create
* read
* update
* edge cases
* persistence
* tool behaviour

Interactive mode is useful for exploratory learning and manual validation.

It is not a substitute for automated testing. Production-quality testing is covered in the hardening checklist.

Interactive loops are a learning aid, not a recommended application architecture.

---

### 9. Prefer framework-native state and orchestration patterns

Reference prompt for bootstrapping a Stateful or Workflow tier agent:

> Build using current LangGraph best practices. Use explicit structured state (typically `AgentState` in LangGraph-native implementations), ToolRuntime, Command(update), ToolMessage where deterministic conversational propagation is required, a suitable checkpointer, thread-based persistence, and clean separation between tools, state, and orchestration.

---

### 10. Use explicit typed domain models where useful

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

Heuristic:

* use raw dicts for small teaching labs and tiny objects with only a few obvious fields
* use dataclasses, Pydantic models, or another typed domain model once fields grow, validation matters, or the object crosses module boundaries

---

### 11. Keep business logic inside tools, not prompts

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

### 12. Treat the LLM as orchestration, not source of truth

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

### 13. Prefer deterministic workflows for production actions

Examples:

* approvals
* ticket resolution
* payments
* provisioning
* compliance flows

Pattern:

```python
validate -> authorise -> execute -> mutate state -> return ToolMessage
```

Avoid:

* hidden prompt logic
* implicit state assumptions
* free-form mutation

---

### 14. Repository learning design principle

One lab should focus on one primary concept.

Examples:

* Lab 01 = isolated message calls
* Lab 03 = custom state
* Lab 05 = persistence
* Lab 06 = tool state access
* Lab 13 = applied stateful workflow capstone

This keeps learning incremental, avoids premature complexity, and makes debugging easier for learners.

---

### 15. Prefer progressive architecture evolution

Recommended sequence:

```text
1. model.invoke
2. create_agent
3. AgentState
4. ToolRuntime
5. Command(update)
6. ToolMessage
7. Checkpointer
8. Deterministic tool workflows
9. Production hardening
```

This maps to four learning tiers:

* Foundation = isolated calls and basic agent concepts
* Stateful = explicit state schema and persistence
* Workflow = tools, runtime state access, and controlled mutations
* Capstone = applied workflows with deterministic controls

This keeps learning incremental and avoids overengineering beginner labs.

---

### 16. Repository learning standard

Architecture expectations depend on the lab tier.

| Tier | Purpose | Expected patterns |
| --- | --- | --- |
| Foundation | Teach one low-level concept clearly | Keep examples simple; use direct model calls or minimal agents when that is the point of the lab. |
| Stateful | Teach structured memory | Use explicit structured state (typically `AgentState` in LangGraph-native labs), stable `thread_id`, and a suitable checkpointer. |
| Workflow | Teach stateful tool behaviour | Add `ToolRuntime`, `Command(update={...})`, `ToolMessage`, and clear separation between tools, state, and orchestration. |
| Capstone | Teach applied production-like workflows | Add deterministic tool workflows, validation, authorisation, observability, and auditable state transitions. |

Foundation labs may be simple. Stateful labs must be architectural. Production-like labs must be deterministic, observable, and auditable.

The standard is principle-led rather than tied only to exact class names. Use the LangGraph-native patterns named above when the lab tier calls for them, but do not force advanced framework machinery into a beginner lab that is intentionally teaching a lower-level concept.

---

### 17. Avoid ad-hoc globals and hidden mutable state

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

## Production Hardening Checklist

Labs teach the core architecture. Production systems require additional hardening.

Add production controls for:

* durable persistence
* state schema versioning and migrations
* idempotency and duplicate tool-call protection
* concurrency and optimistic locking
* input/output validation
* tenant isolation and access control
* secrets handling
* prompt/tool injection protection
* audit trails
* retries, timeouts, backoff, and circuit breakers
* structured logs, trace IDs, metrics, and alerts
* retention, deletion, backup, and restore
* human approval for high-risk actions
* rate limits, cost controls, deployment environments, and rollout strategy

External side effects require explicit control. Persisted state does not guarantee safe external execution. Payments, provisioning, notifications, and destructive actions require explicit validation, authorisation, retries, and failure handling.

Production middleware is a common place to enforce cross-cutting controls such as validation, authorisation, rate limits, logging, retries, observability, and PII filtering.

Production testing should include unit tests, state-transition tests, regression fixtures, integration tests, and adversarial/tool-routing cases.

Production observability should make tool calls, failures, blocked actions, retries, latency, token usage, and state transitions visible.

---

## Common Pitfalls

### Printing historical tool messages repeatedly

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

### Hidden mutable globals

Avoid:

```python
GLOBAL_STATE = {}
```

Problem:
breaks persistence, concurrency, and test isolation. Global mutable state is invisible to the framework and bypasses checkpointing.

---

### Implicit business logic in prompts

Bad pattern:

```text
LLM decides business rules
```

Problem:
Critical rules become nondeterministic. Approval thresholds, access controls, and workflow transitions must live in deterministic tool logic, not prompt instructions.

---

### Blind trust in tool success

Problem:
Assuming a tool execution succeeded without verification leads to inconsistent state when the tool fails silently or partially.

Always validate tool return values before mutating state or propagating `ToolMessage`.

---

### Cross-user thread reuse

Problem:
Reusing `thread_id` across different users or sessions causes state leakage. Each user, tenant, or independent workflow context requires its own unique thread identifier.

---

### Unbounded message history in long-running agents

Problem:
Long-running agents can accumulate excessive message history, causing:

* increased latency
* higher token cost
* context-window exhaustion
* degraded reliability

Mitigations:

* trimming — discard older messages beyond a configurable depth
* summarisation — compress message history into concise summaries
* archival — move older messages to external storage while retaining summaries or key events
* state compaction — fold completed workflow stages into compact state representations

Important:
Token context window constraints are real and must be respected. Mitigations should be designed to preserve operational continuity without implying architectural data loss. Structured workflow state remains the durable source of truth. Message history is conversational context, not the system of record.

---

## Important production principle

The LLM should never be treated as durable memory, workflow authority, or the system of record.

Production systems should persist important state explicitly and enforce critical business rules deterministically through tools, middleware, validation, and structured state transitions.

This is your reference stateful agent learning blueprint.
