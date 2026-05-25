"""
Lab 22: Tool Authorisation Middleware

Purpose: Add the first production control: free users cannot access
premium learning tools.

Key lesson: Middleware can control access outside the tool implementation.
"""

from time import perf_counter

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.shared.tools import (
    create_study_plan,
    explain_topic,
    generate_practice_question,
    grade_answer,
)
from src.part_05_production_middleware.lab_22_tool_authorisation_middleware.middleware import (
    ToolAuthorisationMiddleware,
)

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[
        explain_topic,
        generate_practice_question,
        grade_answer,
        create_study_plan,
    ],
    middleware=[
        ToolAuthorisationMiddleware(user_tier="free"),
    ],
)


def invoke_and_print(prompt: str) -> None:
    """Run the agent once and print the final result."""

    print_turn("user", prompt)

    start_time = perf_counter()

    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    elapsed = perf_counter() - start_time

    for message in response["messages"]:
        role = getattr(message, "type", "unknown")
        content = getattr(message, "content", "")

        if role == "tool" and content:
            print_turn("tool", content)

    final_message = response["messages"][-1]
    print_turn("assistant", final_message.content)
    print(f"[time] invoke() took {elapsed:.2f} seconds\n")


def stream_and_print(prompt: str) -> None:
    """Run the agent with streaming and print tool/assistant updates as they arrive."""

    print_turn("user", prompt)

    start_time = perf_counter()

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        stream_mode="updates",
    ):
        for update in chunk.values():
            messages = update.get("messages", [])
            if not messages:
                continue

            message = messages[-1]
            role = getattr(message, "type", "unknown")
            content = getattr(message, "content", "")

            if not content:
                continue

            if role == "tool":
                print_turn("tool", content)
            elif role == "ai":
                print_turn("assistant", content)

    elapsed = perf_counter() - start_time
    print(f"[time] stream() took {elapsed:.2f} seconds\n")


def main() -> None:
    print_section("22 Tool Authorisation Middleware")

    print_section("Using invoke()")
    invoke_and_print("Create a 7 day study plan for Python decorators")

    print_section("Using stream()")
    stream_and_print("Create a 7 day study plan for Python decorators")

    print_section("What Changed?")
    print(
        "This lab adds the first middleware layer:\n"
        "- Free tools are allowed\n"
        "- Premium tools are blocked for free users\n"
        "- Tool access is now controlled outside the tool itself\n"
        "- The agent can still reason, but middleware controls execution\n"
        "\nLab 23 will add error handling middleware."
    )


if __name__ == "__main__":
    main()
