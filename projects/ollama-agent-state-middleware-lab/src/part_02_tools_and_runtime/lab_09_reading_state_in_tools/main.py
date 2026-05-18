import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class ReadOnlyState(TypedDict):
    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]


class ReadOnlyContext(TypedDict):
    user_id: str
    role: str
    authorised_tools: list[str]


@dataclass(frozen=True)
class ReadOnlyToolRuntime:
    """
    Runtime object for tools that only need to read state.

    The dataclass is frozen to make the runtime reference read-only.
    The state itself is still a dictionary, so this is an educational
    convention rather than full immutability.
    """

    state: ReadOnlyState
    context: ReadOnlyContext

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]


def create_state() -> ReadOnlyState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
            "toolruntime_solution",
        ],
        "current_topic": "reading_state_in_tools",
        "last_action": "started_reading_state_lab",
        "notes": [
            "ToolRuntime groups state and context behind one clean tool interface."
        ],
    }


def create_context() -> ReadOnlyContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "authorised_tools": [
            "read_profile",
            "read_progress",
            "read_next_topic",
        ],
    }


def format_json(data: ReadOnlyState | ReadOnlyContext) -> str:
    return json.dumps(data, indent=2)


def read_profile_tool(runtime: ReadOnlyToolRuntime) -> str:
    tool_name = "read_profile"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    return (
        f"Learner: {runtime.state['learner_name']}\n"
        f"Preferred language: {runtime.state['preferred_language']}\n"
        f"Role: {runtime.context['role']}"
    )


def read_progress_tool(runtime: ReadOnlyToolRuntime) -> str:
    tool_name = "read_progress"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    completed_topics = "\n".join(
        f"- {topic}" for topic in runtime.state["completed_topics"]
    )

    return (
        "Completed topics:\n"
        f"{completed_topics}\n"
        f"Last action: {runtime.state['last_action']}"
    )


def read_next_topic_tool(runtime: ReadOnlyToolRuntime) -> str:
    tool_name = "read_next_topic"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    return f"Current topic: {runtime.state['current_topic']}"


def attempt_unauthorised_read_tool(runtime: ReadOnlyToolRuntime) -> str:
    tool_name = "read_private_admin_notes"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    return "This should not be visible."


def run_profile_read_step(runtime: ReadOnlyToolRuntime) -> None:
    user_message = "Read my learner profile from state."
    tool_result = read_profile_tool(runtime)

    print_section("Step 1: tool reads learner profile")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)


def run_progress_read_step(runtime: ReadOnlyToolRuntime) -> None:
    user_message = "Read my completed topics from state."
    tool_result = read_progress_tool(runtime)

    print_section("Step 2: tool reads learning progress")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)


def run_next_topic_read_step(runtime: ReadOnlyToolRuntime) -> None:
    user_message = "Read my current topic from state."
    tool_result = read_next_topic_tool(runtime)

    print_section("Step 3: tool reads current topic")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)


def run_blocked_read_step(runtime: ReadOnlyToolRuntime) -> None:
    user_message = "Try to read private admin notes."
    tool_result = attempt_unauthorised_read_tool(runtime)

    print_section("Step 4: unauthorised read is blocked")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)


def run_read_only_summary(runtime: ReadOnlyToolRuntime) -> None:
    summary = (
        "Reading state in tools is useful when a tool needs current facts before acting.\n"
        "This lab only reads state. It does not update state.\n"
        f"Current topic remains: {runtime.state['current_topic']}\n"
        f"Last action remains: {runtime.state['last_action']}"
    )

    print_section("Read-only summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("09 Reading State in Tools")

    state = create_state()
    context = create_context()
    runtime = ReadOnlyToolRuntime(state=state, context=context)

    print_turn("initial state", format_json(runtime.state))
    print_turn("runtime context", format_json(runtime.context))

    run_profile_read_step(runtime)
    run_progress_read_step(runtime)
    run_next_topic_read_step(runtime)
    run_blocked_read_step(runtime)
    run_read_only_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Tools can read state to make informed decisions without changing it. "
        "Read-only tools are useful for profile checks, progress checks, permission checks, and routing decisions."
    )


if __name__ == "__main__":
    main()
