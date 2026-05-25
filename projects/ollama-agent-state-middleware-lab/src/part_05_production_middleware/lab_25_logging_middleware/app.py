"""
Lab 25: Logging Middleware

Purpose: Add observability so we can see when the agent starts, when tools run,
and when the agent finishes.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_25_logging_middleware.middleware import (
    LoggingMiddleware,
)
from src.part_05_production_middleware.shared.tools import (
    explain_topic,
    generate_practice_question,
)

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[
        explain_topic,
        generate_practice_question,
    ],
    middleware=[
        LoggingMiddleware(),
    ],
)


def invoke_and_print(prompt: str) -> None:
    print_turn("user", prompt)
    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    for message in response["messages"]:
        role = getattr(message, "type", "unknown")
        content = getattr(message, "content", "")
        if role == "tool" and content:
            print_turn("tool", content)

    final_message = response["messages"][-1]
    print_turn("assistant", final_message.content)
    print()


def main() -> None:
    print_section("25 Logging Middleware")

    invoke_and_print("Explain Python decorators")
    invoke_and_print("Generate a practice question about Python decorators")

    print_section("What Changed?")
    print(
        "This lab adds logging middleware:\n"
        "- Logs agent start/finish timestamps\n"
        "- Logs model input message count\n"
        "- Logs tool start/finish events\n"
        "\nLab 26 will compose multiple middleware layers into a production agent."
    )


if __name__ == "__main__":
    main()

