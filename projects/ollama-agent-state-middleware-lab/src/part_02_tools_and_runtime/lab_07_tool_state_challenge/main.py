import json
from typing import TypedDict

from src.common.printer import print_section, print_turn


class ChallengeState(TypedDict):
    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int
    authorised_tools: list[str]


def create_initial_state() -> ChallengeState:
    return {
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
        ],
        "current_topic": "tool_state_challenge",
        "last_action": "started_tool_state_challenge",
        "notes": [],
        "tool_call_count": 0,
        "authorised_tools": [
            "read_learning_status",
            "add_learning_note",
        ],
    }


def format_state(state: ChallengeState) -> str:
    return json.dumps(state, indent=2)


def check_tool_authorisation(state: ChallengeState, tool_name: str) -> bool:
    """
    Repeated helper required by every tool.

    This is part of the challenge: each tool must remember to check state
    before doing its work.
    """
    return tool_name in state["authorised_tools"]


def increment_tool_count(state: ChallengeState) -> ChallengeState:
    """
    Repeated helper required by every tool.

    This is another part of the challenge: each tool must remember to update
    shared bookkeeping state.
    """
    state["tool_call_count"] += 1
    return state


def read_learning_status_tool(state: ChallengeState) -> str:
    tool_name = "read_learning_status"

    if not check_tool_authorisation(state, tool_name):
        return f"Tool blocked: {tool_name}"

    increment_tool_count(state)

    state["last_action"] = "tool_read_learning_status"

    return (
        f"Learner: {state['learner_name']}\n"
        f"Preferred language: {state['preferred_language']}\n"
        f"Completed topics: {', '.join(state['completed_topics'])}\n"
        f"Current topic: {state['current_topic']}\n"
        f"Tool call count: {state['tool_call_count']}"
    )


def add_learning_note_tool(state: ChallengeState, note: str) -> ChallengeState:
    tool_name = "add_learning_note"

    if not check_tool_authorisation(state, tool_name):
        state["last_action"] = f"blocked_tool:{tool_name}"
        return state

    increment_tool_count(state)

    state["notes"].append(note)
    state["last_action"] = "tool_added_learning_note"

    return state


def complete_topic_tool(state: ChallengeState, topic: str) -> ChallengeState:
    tool_name = "complete_topic"

    if not check_tool_authorisation(state, tool_name):
        state["last_action"] = f"blocked_tool:{tool_name}"
        return state

    increment_tool_count(state)

    if topic not in state["completed_topics"]:
        state["completed_topics"].append(topic)

    state["current_topic"] = "toolruntime_solution"
    state["last_action"] = "tool_completed_topic"

    return state


def run_authorised_read_step(state: ChallengeState) -> None:
    user_message = "Read my learning status with an authorised tool."
    tool_result = read_learning_status_tool(state)

    print_section("Step 1: authorised tool reads state")
    print_turn("user", user_message)
    print_turn("tool result", tool_result)
    print_turn("state", format_state(state))


def run_authorised_write_step(state: ChallengeState) -> ChallengeState:
    user_message = "Add a note with an authorised tool."
    note = "Manual state passing works, but every tool must receive and update state carefully."

    state = add_learning_note_tool(state, note)

    print_section("Step 2: authorised tool writes state")
    print_turn("user", user_message)
    print_turn("written note", note)
    print_turn("state", format_state(state))

    return state


def run_blocked_tool_step(state: ChallengeState) -> ChallengeState:
    user_message = "Try to complete the current topic with an unauthorised tool."

    state = complete_topic_tool(state, "tool_state_challenge")

    print_section("Step 3: unauthorised tool is blocked")
    print_turn("user", user_message)
    print_turn("state", format_state(state))

    return state


def run_challenge_summary(state: ChallengeState) -> None:
    summary = (
        "Manual state passing creates repeated responsibilities:\n"
        "1. Each tool must receive the state argument.\n"
        "2. Each tool must remember to check authorisation.\n"
        "3. Each tool must remember to update shared bookkeeping.\n"
        "4. Each tool can accidentally mutate state in inconsistent ways.\n"
        "5. As tools grow, this pattern becomes noisy and fragile."
    )

    print_section("Challenge summary")
    print_turn("summary", summary)
    print_turn("final state", format_state(state))


def main() -> None:
    print_section("07 Tool State Challenge")

    state = create_initial_state()

    print_turn("initial state", format_state(state))

    run_authorised_read_step(state)
    state = run_authorised_write_step(state)
    state = run_blocked_tool_step(state)
    run_challenge_summary(state)

    print_section("Conclusion")
    print()
    print(
        "Manual state passing is useful for learning, but it does not scale well. "
        "The next lab introduces a runtime-style object so tools can access state through a cleaner interface."
    )


if __name__ == "__main__":
    main()