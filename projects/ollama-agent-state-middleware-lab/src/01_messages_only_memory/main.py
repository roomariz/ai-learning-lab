from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


def run_first_call(model: ChatOllama) -> None:
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

    response = model.invoke(messages)

    print_section("Call 1: user shares a preference")
    print_turn("user", messages[-1][1])
    print_turn("assistant", response.content)


def run_second_call_without_history(model: ChatOllama) -> None:
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

    response = model.invoke(messages)

    print_section("Call 2: fresh call without previous messages")
    print_turn("user", messages[-1][1])
    print_turn("assistant", response.content)


def main() -> None:
    print_section("01 Messages-Only Memory")

    model = get_chat_model()

    run_first_call(model)
    run_second_call_without_history(model)

    print_section("Conclusion")
    print(
        "The second call does not include the first message. "
        "The model therefore has no reliable way to know the user's preference. "
        "This is the core limitation of messages-only memory."
    )


if __name__ == "__main__":
    main()