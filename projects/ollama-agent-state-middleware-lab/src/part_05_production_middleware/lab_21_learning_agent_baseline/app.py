"""
Lab 21: Learning Agent Baseline

Purpose: Build the simplest working Ollama-powered learning agent with
LangChain create_agent() and no middleware yet.

Key lesson: Without middleware —
  - Premium tools are freely accessible
  - No input validation
  - No logging / observability
  - No retries on failure
  - No message trimming
  - No production safety guards

This is the exact baseline that Lab 22–26 will wrap with middleware layers.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.shared.tools import (
    create_study_plan,
    explain_topic,
    generate_practice_question,
    grade_answer,
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
)


def invoke_and_print(prompt: str) -> None:
    """Run the agent with streaming and print visible AI/tool messages."""

    print_turn("user", prompt)

    stream = agent.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        stream_mode="updates",
    )

    for chunk in stream:
        for update in chunk.values():
            messages = update.get("messages", [])

            if not messages:
                continue

            message = messages[-1]
            role = getattr(message, "type", "unknown")
            content = getattr(message, "content", "")

            if not content:
                continue

            if role == "ai":
                print_turn("assistant", content)
            elif role == "tool":
                print_turn("tool", content)

    print()

def main() -> None:
    print_section("21 Learning Agent Baseline (No Middleware)")

    invoke_and_print("Explain what a Python decorator is")
    invoke_and_print("Create a 7 day study plan for Python decorators")
    invoke_and_print("Generate a practice question about Python decorators")

    print_section("No Middleware — What's Missing?")
    print(
        "This baseline runs with zero production safeguards:\n"
        "- All four tools are freely callable (no authz)\n"
        "- No validation: empty, huge, or malicious input goes straight through\n"
        "- No logging: zero observability into agent decisions\n"
        "- No retries: a single tool failure kills the call\n"
        "- No trimming: long message histories are not shortened before the model runs\n"
        "- No error boundaries: unhandled exceptions crash the agent\n"
        "\nLab 22 will add tool authorisation middleware."
    )


if __name__ == "__main__":
    main()
