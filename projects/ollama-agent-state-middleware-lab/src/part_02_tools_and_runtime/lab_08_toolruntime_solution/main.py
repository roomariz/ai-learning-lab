import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class RuntimeState(TypedDict):
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
    authorised_tools: list[str]


# ToolRuntime groups state and context behind one clean interface.
# This separates orchestration (passing runtime) from tool logic (using runtime).
# Production agents use this pattern to keep tools focused on their domain.
@dataclass
class ToolRuntime:
    """
    Small educational runtime object.

    It groups state and context so tools do not need several separate
    arguments or repeated global lookups.
    """

    state: RuntimeState
    context: RuntimeContext

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action


def create_initial_state() -> RuntimeState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
        ],
        "current_topic": "toolruntime_solution",
        "last_action": "started_toolruntime_solution",
        "notes": [],
        "tool_call_count": 0,
    }


def create_runtime_context() -> RuntimeContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "authorised_tools": [
            "read_learning_status",
            "add_learning_note",
            "complete_topic",
        ],
    }


def format_json(data: RuntimeState | RuntimeContext) -> str:
    return json.dumps(data, indent=2)


def read_learning_status_tool(runtime: ToolRuntime) -> str:
    tool_name = "read_learning_status"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.record_tool_call("tool_read_learning_status")

    state = runtime.state
    context = runtime.context

    return (
        f"User ID: {context['user_id']}\n"
        f"Role: {context['role']}\n"
        f"Learner: {state['learner_name']}\n"
        f"Preferred language: {state['preferred_language']}\n"
        f"Completed topics: {', '.join(state['completed_topics'])}\n"
        f"Current topic: {state['current_topic']}\n"
        f"Tool call count: {state['tool_call_count']}"
    )


def add_learning_note_tool(runtime: ToolRuntime, note: str) -> None:
    tool_name = "add_learning_note"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return

    runtime.state["notes"].append(note)
    runtime.record_tool_call("tool_added_learning_note")


def complete_topic_tool(runtime: ToolRuntime, topic: str, next_topic: str) -> None:
    tool_name = "complete_topic"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return

    if topic not in runtime.state["completed_topics"]:
        runtime.state["completed_topics"].append(topic)

    runtime.state["current_topic"] = next_topic
    runtime.record_tool_call("tool_completed_topic")


def run_read_step(runtime: ToolRuntime) -> None:
    user_message = "Use the runtime object to read my learning status."
    tool_result = read_learning_status_tool(runtime)

    print_section("Step 1: tool reads through runtime")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_write_note_step(runtime: ToolRuntime) -> None:
    user_message = "Use the runtime object to add a learning note."
    note = "ToolRuntime groups state and context behind one clean tool interface."

    add_learning_note_tool(runtime, note)

    print_section("Step 2: tool writes through runtime")
    print_turn("user", user_message)
    print_turn("written note", note)
    print_turn("state", format_json(runtime.state))


def run_complete_topic_step(runtime: ToolRuntime) -> None:
    user_message = "Complete the ToolRuntime solution lab."

    complete_topic_tool(
        runtime=runtime,
        topic="toolruntime_solution",
        next_topic="reading_state_in_tools",
    )

    print_section("Step 3: tool updates progress through runtime")
    print_turn("user", user_message)
    print_turn("state", format_json(runtime.state))


def run_runtime_summary(runtime: ToolRuntime) -> None:
    summary = (
        "The runtime object gives tools one controlled interface:\n"
        f"User ID: {runtime.context['user_id']}\n"
        f"Role: {runtime.context['role']}\n"
        f"Completed topic: toolruntime_solution\n"
        f"Current topic: {runtime.state['current_topic']}\n"
        f"Tool call count: {runtime.state['tool_call_count']}\n"
        f"Last action: {runtime.state['last_action']}"
    )

    print_section("Runtime summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))
    print_turn("context", format_json(runtime.context))


def main() -> None:
    print_section("08 ToolRuntime Solution")

    state = create_initial_state()
    context = create_runtime_context()
    runtime = ToolRuntime(state=state, context=context)

    print_turn("initial state", format_json(runtime.state))
    print_turn("runtime context", format_json(runtime.context))

    run_read_step(runtime)
    run_write_note_step(runtime)
    run_complete_topic_step(runtime)
    run_runtime_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "A runtime object reduces repetitive manual state passing. "
        "Tools can use one interface to read state, write state, check context, and record actions."
    )


if __name__ == "__main__":
    main()