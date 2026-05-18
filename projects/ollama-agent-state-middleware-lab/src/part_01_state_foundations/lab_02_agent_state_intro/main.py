from typing import TypedDict

from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class AgentState(TypedDict):
    preferred_language: str | None


def save_preference_to_state(state: AgentState, preferred_language: str) -> AgentState:
    """
    Store an important user fact in structured state.

    This is deliberately simple. Later labs will show persistence,
    custom state schemas, and tool-based state updates.
    """
    state["preferred_language"] = preferred_language
    return state


def run_first_call(model: ChatOllama, state: AgentState) -> AgentState:
    user_message = "My preferred programming language is Python. Please remember that."

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "When the user shares a preference, acknowledge it briefly.",
        ),
        (
            "human",
            user_message,
        ),
    ]

    response = model.invoke(messages)

    state = save_preference_to_state(state, preferred_language="Python")

    print_section("Call 1: user shares a preference")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("state", str(state))

    return state


def run_second_call_with_state(model: ChatOllama, state: AgentState) -> None:
    user_message = "What is my preferred programming language?"

    preferred_language = state.get("preferred_language")

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Use the provided state when answering the user.",
        ),
        (
            "human",
            (
                f"Current agent state: preferred_language={preferred_language}\n\n"
                f"User question: {user_message}"
            ),
        ),
    ]

    response = model.invoke(messages)

    print_section("Call 2: fresh call with structured state")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("state", str(state))


def main() -> None:
    print_section("02 Agent State Intro")

    model = get_chat_model()

    state: AgentState = {
        "preferred_language": None,
    }

    state = run_first_call(model, state)
    run_second_call_with_state(model, state)

    print_section("Conclusion")
    print(
        "The second call still does not include the full earlier conversation. "
        "However, it receives the important fact through structured state. "
        "This shows why agent state is more reliable than relying only on raw message history."
    )


if __name__ == "__main__":
    main()