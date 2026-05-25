"""
Lab 24: Message Trimming Middleware

Purpose: Keep long conversations manageable before they reach the model.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_24_message_trimming_middleware.middleware import (
    MessageTrimmingMiddleware,
)
from src.part_05_production_middleware.shared.tools import explain_topic


model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[explain_topic],
    middleware=[MessageTrimmingMiddleware(max_messages=3)],
)


def invoke_and_print(messages: list[dict[str, str]]) -> None:
    print_turn("messages", f"{len(messages)} total")

    response = agent.invoke({"messages": messages})  # type: ignore[arg-type]

    final_message = response["messages"][-1]
    content = getattr(final_message, "content", "")

    if content:
        print_turn("assistant", content)
    else:
        print_turn("assistant", "[no response]")

    print()


def main() -> None:
    print_section("24 Message Trimming Middleware")

    print_section("Example 1: Final User Request Survives")

    request_survives: list[dict[str, str]] = [
        {"role": "user", "content": "Explain Python decorators"},
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Message 3"},
        {"role": "assistant", "content": "Response 3"},
        {"role": "user", "content": "Explain Python decorators"},
    ]

    print(
        "max_messages=3 keeps the latest 3 messages.\n"
        "The first five messages are removed.\n"
        "The final user request remains, so the agent can answer.\n"
    )

    invoke_and_print(request_survives)

    print_section("Example 2: No Fresh User Request")

    request_missing: list[dict[str, str]] = [
        {"role": "user", "content": "Explain Python decorators"},
        {"role": "assistant", "content": "Decorators wrap functions."},
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
    ]

    print(
        "max_messages=3 keeps the latest 3 messages.\n"
        "The real request about decorators is removed.\n"
        "The remaining input contains only placeholder messages.\n"
        "The agent may produce an empty or confusing response.\n"
    )

    invoke_and_print(request_missing)

    print_section("Why Order Matters")
    print(
        "If the last message is an assistant message, the agent may have no fresh user request.\n"
        "That can produce an empty or confusing response.\n"
        "\nCorrect pattern:\n"
        "- old user message\n"
        "- old assistant response\n"
        "- latest user request\n"
        "\nAvoid ending the input with an old assistant response."
    )

    print_section("What Changed?")
    print(
        "This lab adds message trimming middleware:\n"
        "- Large message histories are cut down before the model runs\n"
        "- Old messages at the top are removed first\n"
        "- Recent messages at the bottom are kept\n"
        "- The final user request should normally be the last message\n"
        "- If the final user request is trimmed away, the agent may not know what to answer\n"
        "- The agent remains functional while context stays bounded\n"
        "\nLab 25 will add logging middleware."
    )


if __name__ == "__main__":
    main()