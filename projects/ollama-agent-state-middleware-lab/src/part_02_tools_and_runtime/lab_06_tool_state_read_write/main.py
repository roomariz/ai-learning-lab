import json
from typing import TypedDict

from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class ToolLearningState(TypedDict):
    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None
    notes: list[str]


def create_initial_state() -> ToolLearningState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": ["custom_state", "state_persistence"],
        "current_topic": "tool_state_read_write",
        "last_action": "started_tool_state_lab",
        "notes": [],
    }


def format_state(state: ToolLearningState) -> str:
    return json.dumps(state, indent=2)


def read_learning_status_tool(state: ToolLearningState) -> str:
    """
    Tool that reads from state.

    This imitates a tool needing access to current agent state before
    deciding what to return.
    """
    return (
        f"Learner: {state['learner_name']}\n"
        f"Preferred language: {state['preferred_language']}\n"
        f"Completed topics: {', '.join(state['completed_topics'])}\n"
        f"Current topic: {state['current_topic']}"
    )


def write_learning_note_tool(state: ToolLearningState, note: str) -> ToolLearningState:
    """
    Tool that writes to state.

    This imitates a tool updating structured agent state after an action.
    """
    state["notes"].append(note)
    state["last_action"] = "tool_added_learning_note"
    return state


def complete_topic_tool(state: ToolLearningState, topic: str) -> ToolLearningState:
    """
    Tool that updates progress in state.
    """
    if topic not in state["completed_topics"]:
        state["completed_topics"].append(topic)

    state["current_topic"] = "toolruntime_solution"
    state["last_action"] = "tool_completed_topic"

    return state


def run_read_tool_step(model: ChatOllama, state: ToolLearningState) -> None:
    user_message = "Use a tool to read my current learning status."

    tool_result = read_learning_status_tool(state)

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Use only the supplied tool result. "
            "Reply in two short sentences.",
        ),
        (
            "human",
            (
                f"Tool result:\n{tool_result}\n\n"
                f"User question: {user_message}"
            ),
        ),
    ]

    response = model.invoke(messages)

    print_section("Step 1: tool reads from state")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("assistant", response.content)


def run_write_note_tool_step(state: ToolLearningState) -> ToolLearningState:
    user_message = "Add a note that tools can update structured state."

    note = "Tools can read from and write to structured agent state."
    state = write_learning_note_tool(state, note)

    print_section("Step 2: tool writes a note to state")
    print_turn("user", user_message)
    print_turn("written note", note)
    print_turn("state", format_state(state))

    return state


def run_complete_topic_tool_step(state: ToolLearningState) -> ToolLearningState:
    user_message = "Mark the tool state read/write lab as complete."

    state = complete_topic_tool(state, "tool_state_read_write")

    print_section("Step 3: tool updates progress in state")
    print_turn("user", user_message)
    print_turn("state", format_state(state))

    return state


def run_final_summary(state: ToolLearningState) -> None:
    user_message = "Summarise what changed after the tools ran."

    completed_topic = "tool_state_read_write"
    current_topic = state["current_topic"]
    last_note = state["notes"][-1] if state["notes"] else "No note was added."
    last_action = state["last_action"]

    summary = (
        f"The tools added this note: {last_note}\n"
        f"The completed topic is now: {completed_topic}\n"
        f"The current topic is now: {current_topic}\n"
        f"The last action is now: {last_action}"
    )

    print_section("Step 4: deterministic summary of updated state")
    print_turn("user", user_message)
    print_turn("summary", summary)
    print_turn("final state", format_state(state))


def main() -> None:
    print_section("06 Tool State Read Write")

    model = get_chat_model()
    state = create_initial_state()

    print_turn("initial state", format_state(state))

    run_read_tool_step(model, state)
    state = run_write_note_tool_step(state)
    state = run_complete_topic_tool_step(state)
    run_final_summary(state)

    print_section("Conclusion")
    print()
    print(
        "Tools often need access to agent state. "
        "A read tool can inspect state, while a write tool can update state after an action. "
        "This lab passes state manually so the data flow is easy to see."
    )


if __name__ == "__main__":
    main()