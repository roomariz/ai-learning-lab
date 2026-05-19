# Part 02: Tools and Runtime

This section introduces framework-native tools, runtime access, and state management using LangGraph agents.

The labs progressively move from tool-state access toward clear runtime, read/write, and context/state boundaries.

## Learning progression

| Lab | Focus                   | Key concept                               |
| --- | ----------------------- | ----------------------------------------- |
| 06  | Tool state read/write   | Tools interact with persisted state       |
| 07  | Tool state challenge    | Manual state passing anti-pattern         |
| 08  | ToolRuntime solution    | Framework-injected runtime access         |
| 09  | Reading state           | Read-only access to `runtime.state`       |
| 10  | Writing state           | `Command(update={...})` state mutation    |
| 11  | Context vs state        | Stable metadata vs mutable workflow state |

---

## Labs

### Lab 06 — Tool State Read Write

**Goal:** Show how tools can read from and write to structured `AgentState` using framework-native patterns.

**Learning focus:**
* `@tool`
* `create_agent`
* Tool invocation
* Model-driven tool selection
* Basic agent execution

**Files:**
```txt
lab_06_tool_state_read_write/
├── README.md
├── main.py
└── expected_output.txt
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_06_tool_state_read_write.main
```

**Learning point:** Tools let agents perform structured actions outside the language model.

---

### Lab 07 — Tool State Challenge

**Goal:** Show why manually passing state into every tool becomes awkward and fragile.

**Learning focus:**
* Manual state passing
* Repeated authorisation checks
* Repeated bookkeeping updates
* Direct mutation risks
* Why `ToolRuntime` is needed

**Files:**
```txt
lab_07_tool_state_challenge/
├── README.md
├── main.py
└── expected_output.txt
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_07_tool_state_challenge.main
```

**Learning point:** Manual state passing becomes noisy and fragile as tool workflows grow.

---

### Lab 08 — ToolRuntime Solution

**Goal:** Show how framework-injected `ToolRuntime` gives tools clean access to agent state.

**Learning focus:**
* `ToolRuntime`
* Runtime state access
* Runtime metadata
* Shared runtime interface

**Files:**
```txt
lab_08_toolruntime_solution/
├── README.md
├── main.py
└── expected_output.txt
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_08_toolruntime_solution.main
```

**Learning point:** `ToolRuntime` gives tools structured access to execution state and runtime metadata.

---

### Lab 09 — Reading State in Tools

**Goal:** Show how tools can read `AgentState` through framework-injected `ToolRuntime` without mutating state.

**Learning focus:**
* `runtime.state`
* Read-only tool patterns
* Authorisation checks
* State inspection
* `MemorySaver`
* Persistent threads

**Files:**
```txt
lab_09_reading_state_in_tools/
├── README.md
├── main.py
└── expected_output.txt
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_09_reading_state_in_tools.main
```

**Learning point:** Not every tool should modify state. Many tools only need to inspect state before responding.

---

### Lab 10 — Writing State from Tools

**Goal:** Show how tools update `AgentState` using `Command(update={...})`.

**Learning focus:**
* `Command(update={...})`
* Atomic state updates
* `ToolMessage`
* Persistent state mutation
* Controlled write patterns

**Files:**
```txt
lab_10_writing_state_from_tools/
├── README.md
├── main.py
└── expected_output.txt
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_10_writing_state_from_tools.main
```

**Learning point:** Write tools deliberately change future agent behaviour through controlled state updates.

---

### Lab 11 — Context vs State

**Goal:** Show the difference between stable runtime context and mutable agent state.

**Learning focus:**
* `AgentState`
* Runtime metadata
* Stable context
* Mutable workflow state
* Separation of concerns

**Files:**
```txt
lab_11_context_vs_state/
├── README.md
└── main.py
```

**Run:**
```bash
uv run python -m src.part_02_tools_and_runtime.lab_11_context_vs_state.main
```

**Learning point:**

Context answers:
* Who is using the system?
* Under what role?
* In which environment?

State answers:
* What happened so far?
* What is the agent currently doing?
* What should happen next?

---

## Recommended learning order

Follow the labs sequentially:

```txt
06 → 07 → 08 → 09 → 10 → 11
```

Each lab builds directly on the previous concepts.

---

## Key architectural progression

| Stage                  | Concept                            |
| ---------------------- | ---------------------------------- |
| Basic tools            | Register and invoke tools          |
| Runtime access         | Inject runtime into tools          |
| Read state             | Inspect workflow state             |
| Write state            | Persist workflow changes           |
| Separate context/state | Clean architecture boundaries      |

---

## Core concepts introduced

| Concept                     | Introduced |
| --------------------------- | ---------- |
| `@tool`                     | Lab 06     |
| Manual state passing challenge | Lab 07     |
| `ToolRuntime`               | Lab 08     |
| Read-only state access      | Lab 09     |
| `Command(update={...})`     | Lab 10     |
| Context vs state separation | Lab 11     |

---

## Important design principles

1. **State should be structured** — Use typed `AgentState` fields instead of unstructured dictionaries.

2. **Tools should be explicit** — Tools should have deterministic responsibilities and predictable side effects.

3. **Reads and writes should be separated** — Read-only tools are safer than write tools. Write tools should use controlled update patterns.

4. **Context and state are different** — Stable metadata should not be mixed into mutable workflow state.

5. **Runtime access should be framework-managed** — Tools should use `ToolRuntime` rather than manually passing state through every function.