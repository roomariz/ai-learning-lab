from typing import TypedDict

from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class LearningAgentState(TypedDict):
    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None


def create_initial_state() -> LearningAgentState:
    return {
        "learner_name": None,
        "preferred_language": None,
        "completed_topics": [],
        "current_topic": None,
        "last_action": None,
    }


def update_learning_state(
    state: LearningAgentState,
    learner_name: str,
    preferred_language: str,
    completed_topic: str,
    current_topic: str,
    last_action: str,
) -> LearningAgentState:
    state["learner_name"] = learner_name
    state["preferred_language"] = preferred_language

    if completed_topic not in state["completed_topics"]:
        state["completed_topics"].append(completed_topic)

    state["current_topic"] = current_topic
    state["last_action"] = last_action

    return state


def run_first_call(model: ChatOllama, state: LearningAgentState) -> LearningAgentState:
    user_message = (
        "My name is Muhammad. My preferred programming language is Python. "
        "I have completed the agent state intro lab. Now I want to study custom state."
    )

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Reply in one short sentence. "
            "Acknowledge the learner's progress and next topic only.",
        ),
        (
            "human",
            user_message,
        ),
    ]

    response = model.invoke(messages)

    state = update_learning_state(
        state=state,
        learner_name="Muhammad",
        preferred_language="Python",
        completed_topic="agent_state_intro",
        current_topic="custom_state",
        last_action="updated_learning_profile",
    )

    print_section("Call 1: user shares learning profile")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("state", str(state))

    return state


def run_second_call_with_custom_state(
    model: ChatOllama,
    state: LearningAgentState,
) -> None:
    user_message = "Summarise my current learning status."

    state_summary = (
        f"learner_name={state['learner_name']}\n"
        f"preferred_language={state['preferred_language']}\n"
        f"completed_topics={state['completed_topics']}\n"
        f"current_topic={state['current_topic']}\n"
        f"last_action={state['last_action']}"
    )

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Use the provided custom state to answer the user. "
            "Do not invent facts that are not in the state.",
        ),
        (
            "human",
            (
                f"Current custom agent state:\n{state_summary}\n\n"
                f"User question: {user_message}"
            ),
        ),
    ]

    response = model.invoke(messages)

    print_section("Call 2: fresh call with custom state")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("state", str(state))


def main() -> None:
    print_section("03 Custom State")

    model = get_chat_model()
    state = create_initial_state()

    state = run_first_call(model, state)
    run_second_call_with_custom_state(model, state)

    print_section("Conclusion")
    print()
    print(
        "Custom state lets the program track several structured facts at once. "
        "This is more useful than storing one isolated value. "
        "It gives the agent controlled access to the learner's profile, progress, current topic, and last action."
    )


if __name__ == "__main__":
    main()