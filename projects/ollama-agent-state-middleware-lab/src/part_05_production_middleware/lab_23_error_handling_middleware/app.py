"""
Lab 23: Error Handling Middleware

Purpose: Catch tool failures and return safe, learner-friendly error messages
instead of crashing the agent.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_23_error_handling_middleware.middleware import (
    handle_tool_errors,
)
from src.part_05_production_middleware.lab_23_error_handling_middleware.tools import (
    broken_quiz_generator,
)
from src.part_05_production_middleware.shared.tools import explain_topic

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[
        explain_topic,
        broken_quiz_generator,
    ],
    middleware=[
        handle_tool_errors,
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
    print_section("23 Error Handling Middleware")

    print_section("Normal Tool Still Works")
    invoke_and_print("Explain Python decorators")

    print_section("Broken Tool Is Handled Safely")
    invoke_and_print("Use broken_quiz_generator for Python decorators")

    print_section("What Changed?")
    print(
        "This lab adds error-handling middleware:\n"
        "- Normal tools still run as before\n"
        "- Tool exceptions are caught by middleware\n"
        "- Failed tools return a safe ToolMessage instead of crashing the agent\n"
        "- The agent can continue and explain the failure to the learner\n"
        "\nLab 24 will add message trimming middleware."
    )


if __name__ == "__main__":
    main()
