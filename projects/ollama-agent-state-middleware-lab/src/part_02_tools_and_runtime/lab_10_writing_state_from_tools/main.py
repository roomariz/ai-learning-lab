import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class WritableState(TypedDict):
    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int


class WritableContext(TypedDict):
    user_id: str
    role: str
    authorised_tools: list[str]


@dataclass
class WritableToolRuntime:
    """
    Runtime object for tools that are allowed to write to state.

    Unlike the read-only runtime in Lab 09, this runtime deliberately exposes
    methods that mutate state in controlled ways.
    """

    state: WritableState
    context: WritableContext

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action

    def add_note(self, note: str) -> None:
        self.state["notes"].append(note)

    def complete_topic(self, topic: str, next_topic: str) -> None:
        if topic not in self.state["completed_topics"]:
            self.state["completed_topics"].append(topic)

        self.state["current_topic"] = next_topic


def create_state() -> WritableState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
            "toolruntime_solution",
            "reading_state_in_tools",
        ],
        "current_topic": "writing_state_from_tools",
        "last_action": "started_writing_state_lab",
        "notes": [
            "Reading tools should inspect state without mutating it."
        ],
        "tool_call_count": 0,
    }


def create_context() -> WritableContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "authorised_tools": [
            "add_learning_note",
            "complete_topic",
            "set_next_topic",
        ],
    }


def format_json(data: WritableState | WritableContext) -> str:
    return json.dumps(data, indent=2)


def add_learning_note_tool(runtime: WritableToolRuntime, note: str) -> str:
    tool_name = "add_learning_note"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.add_note(note)
    runtime.record_tool_call("tool_added_learning_note")

    return f"Note added: {note}"


def complete_topic_tool(
    runtime: WritableToolRuntime,
    topic: str,
    next_topic: str,
) -> str:
    tool_name = "complete_topic"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.complete_topic(topic=topic, next_topic=next_topic)
    runtime.record_tool_call("tool_completed_topic")

    return f"Completed {topic}; next topic is {next_topic}."


def set_next_topic_tool(runtime: WritableToolRuntime, next_topic: str) -> str:
    tool_name = "set_next_topic"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.state["current_topic"] = next_topic
    runtime.record_tool_call("tool_set_next_topic")

    return f"Current topic set to {next_topic}."


def blocked_admin_write_tool(runtime: WritableToolRuntime) -> str:
    tool_name = "delete_all_notes"

    if not runtime.is_tool_authorised(tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name}"

    runtime.state["notes"].clear()
    runtime.record_tool_call("tool_deleted_all_notes")

    return "All notes deleted."


def run_add_note_step(runtime: WritableToolRuntime) -> None:
    user_message = "Add a note about writing state from tools."
    note = "Writing tools should update state through controlled runtime methods."

    tool_result = add_learning_note_tool(runtime, note)

    print_section("Step 1: tool writes a note")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_complete_topic_step(runtime: WritableToolRuntime) -> None:
    user_message = "Complete the writing state from tools lab."

    tool_result = complete_topic_tool(
        runtime=runtime,
        topic="writing_state_from_tools",
        next_topic="context_vs_state",
    )

    print_section("Step 2: tool completes topic")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_set_next_topic_step(runtime: WritableToolRuntime) -> None:
    user_message = "Set the next topic to context versus state."

    tool_result = set_next_topic_tool(runtime, "context_vs_state")

    print_section("Step 3: tool sets next topic")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_blocked_write_step(runtime: WritableToolRuntime) -> None:
    user_message = "Try to delete all notes."

    tool_result = blocked_admin_write_tool(runtime)

    print_section("Step 4: unauthorised write is blocked")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_json(runtime.state))


def run_write_summary(runtime: WritableToolRuntime) -> None:
    summary = (
        "Writing state from tools changed the agent state in controlled ways:\n"
        f"Tool call count: {runtime.state['tool_call_count']}\n"
        f"Completed topic added: writing_state_from_tools\n"
        f"Current topic: {runtime.state['current_topic']}\n"
        f"Last action: {runtime.state['last_action']}\n"
        f"Notes count: {len(runtime.state['notes'])}"
    )

    print_section("Write summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("10 Writing State from Tools")

    state = create_state()
    context = create_context()
    runtime = WritableToolRuntime(state=state, context=context)

    print_turn("initial state", format_json(runtime.state))
    print_turn("runtime context", format_json(runtime.context))

    run_add_note_step(runtime)
    run_complete_topic_step(runtime)
    run_set_next_topic_step(runtime)
    run_blocked_write_step(runtime)
    run_write_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Writing tools intentionally change state. "
        "A runtime object gives the project one controlled place for common write operations such as adding notes, completing topics, and recording actions."
    )


if __name__ == "__main__":
    main()
