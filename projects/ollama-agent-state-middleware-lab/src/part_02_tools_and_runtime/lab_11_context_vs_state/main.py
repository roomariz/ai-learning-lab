import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


# State vs Context: A key architectural separation in production agents.
# - State: changes during the agent run (current_topic, notes, tool_call_count)
# - Context: stable info for this run (user_id, role, tenant_id, environment)
# This separation makes tools easier to reason about and enables proper persistence.
class AgentState(TypedDict):
    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int


class RuntimeContext(TypedDict):
    user_id: str
    role: str
    tenant_id: str
    environment: str
    authorised_tools: list[str]


@dataclass
class Runtime:
    state: AgentState
    context: RuntimeContext

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action

    def add_note(self, note: str) -> None:
        self.state["notes"].append(note)


def create_state() -> AgentState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
            "toolruntime_solution",
            "reading_state_in_tools",
            "writing_state_from_tools",
        ],
        "current_topic": "context_vs_state",
        "last_action": "started_context_vs_state_lab",
        "notes": [
            "State changes during the agent run."
        ],
        "tool_call_count": 0,
    }


def create_context() -> RuntimeContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "tenant_id": "learning-lab",
        "environment": "local",
        "authorised_tools": [
            "explain_context",
            "explain_state",
            "add_state_note",
        ],
    }


def format_json(data: AgentState | RuntimeContext) -> str:
    return json.dumps(data, indent=2)


def explain_context_tool(runtime: Runtime) -> str:
    tool_name = "explain_context"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.record_tool_call("tool_explained_context")

    return (
        "Context is stable information supplied to this run.\n"
        f"User ID: {runtime.context['user_id']}\n"
        f"Role: {runtime.context['role']}\n"
        f"Tenant ID: {runtime.context['tenant_id']}\n"
        f"Environment: {runtime.context['environment']}"
    )


def explain_state_tool(runtime: Runtime) -> str:
    tool_name = "explain_state"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.record_tool_call("tool_explained_state")

    return (
        "State is changing information tracked during the agent run.\n"
        f"Learner: {runtime.state['learner_name']}\n"
        f"Current topic: {runtime.state['current_topic']}\n"
        f"Completed topics count: {len(runtime.state['completed_topics'])}\n"
        f"Notes count: {len(runtime.state['notes'])}\n"
        f"Tool call count: {runtime.state['tool_call_count']}"
    )


def add_state_note_tool(runtime: Runtime, note: str) -> str:
    tool_name = "add_state_note"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.add_note(note)
    runtime.record_tool_call("tool_added_state_note")

    return f"State note added: {note}"


def run_context_step(runtime: Runtime) -> None:
    user_message = "Explain the runtime context."

    tool_result = explain_context_tool(runtime)

    print_section("Step 1: tool reads context")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("context", format_json(runtime.context))
    print_turn("state", format_json(runtime.state))


def run_state_step(runtime: Runtime) -> None:
    user_message = "Explain the current state."

    tool_result = explain_state_tool(runtime)

    print_section("Step 2: tool reads state")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_state_write_step(runtime: Runtime) -> None:
    user_message = "Add a note to state."
    note = "Context should stay stable while state may change."

    tool_result = add_state_note_tool(runtime, note)

    print_section("Step 3: tool writes state, not context")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("context", format_json(runtime.context))
    print_turn("state", format_json(runtime.state))


def run_comparison_summary(runtime: Runtime) -> None:
    summary = (
        "Context and state have different jobs:\n"
        "Context: stable run information, such as user_id, role, tenant_id, and environment.\n"
        "State: changing agent information, such as current_topic, notes, last_action, and tool_call_count.\n"
        f"Context role remains: {runtime.context['role']}\n"
        f"State last action is now: {runtime.state['last_action']}\n"
        f"State notes count is now: {len(runtime.state['notes'])}"
    )

    print_section("Context vs state summary")
    print_turn("summary", summary)
    print_turn("final context", format_json(runtime.context))
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("11 Context vs State")

    state = create_state()
    context = create_context()
    runtime = Runtime(state=state, context=context)

    print_turn("initial context", format_json(runtime.context))
    print_turn("initial state", format_json(runtime.state))

    run_context_step(runtime)
    run_state_step(runtime)
    run_state_write_step(runtime)
    run_comparison_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Context is stable information supplied to the run. "
        "State is information that changes as the agent works. "
        "Keeping them separate makes tools easier to reason about."
    )


if __name__ == "__main__":
    main()