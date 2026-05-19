"""
Lab 01: Messages-Only Memory

This lab demonstrates that each model.invoke() call is isolated.
There's no automatic memory between calls - the model only sees the
messages passed in the current invocation.

Later labs introduce AgentState and persistence as stronger memory patterns.
"""

from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


def message_content_to_str(content: object) -> str:
    """Convert message content to string regardless of its type."""
    if isinstance(content, str):
        return content
    return str(content)


def invoke_model(model: ChatOllama, messages: list[tuple[str, str]]) -> str:
    """Call the model with a list of (role, content) message tuples."""
    try:
        response = model.invoke(messages)
    except Exception:
        return "Model call failed safely. Check your local model configuration."

    return message_content_to_str(response.content)


def run_first_call(model: ChatOllama) -> None:
    """First call: User tells the model their preferred language."""
    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "When the user shares a preference, acknowledge it briefly.",
        ),
        (
            "human",
            "My preferred programming language is Python. Please remember that.",
        ),
    ]

    print_section("Call 1: user shares a preference")
    print_turn("user", messages[-1][1])

    assistant_message = invoke_model(model, messages)
    print_turn("assistant", assistant_message)


def run_second_call_without_history(model: ChatOllama) -> None:
    """
    Second call: Ask about the preference WITHOUT including first call's messages.
    The model has no memory of the previous call.
    """
    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Answer only from the information available in this current call.",
        ),
        (
            "human",
            "What is my preferred programming language?",
        ),
    ]

    print_section("Call 2: fresh call without previous messages")
    print_turn("user", messages[-1][1])

    assistant_message = invoke_model(model, messages)
    print_turn("assistant", assistant_message)


def main() -> None:
    print_section("01 Messages-Only Memory")

    model = get_chat_model()

    run_first_call(model)
    run_second_call_without_history(model)

    print_section("Conclusion")
    print(
        "The second call does not include the first message. "
        "The model therefore has no reliable way to know the user's preference. "
        "This is the core limitation of isolated message calls: "
        "the model only sees the messages passed into the current invocation."
    )


if __name__ == "__main__":
    main()