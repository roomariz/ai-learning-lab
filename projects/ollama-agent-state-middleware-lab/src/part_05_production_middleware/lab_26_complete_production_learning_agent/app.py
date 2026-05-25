"""
Lab 26: Complete Production Learning Agent

Purpose: Compose multiple middleware layers into one production-style agent.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_26_complete_production_learning_agent.middleware import (
    production_middleware,
)
from src.part_05_production_middleware.shared.tools import (
    broken_quiz_generator,
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
        broken_quiz_generator,
    ],
    middleware=production_middleware(),
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


def invoke_messages_and_print(messages: list[dict[str, str]]) -> None:
    print_turn("messages", f"{len(messages)} total")
    response = agent.invoke({"messages": messages})

    final_message = response["messages"][-1]
    print_turn("assistant", final_message.content)
    print()


def main() -> None:
    print_section("26 Complete Production Learning Agent (Capstone)")

    print_section("Scenario 1: normal request")
    invoke_and_print("Explain Python decorators")

    print_section("Scenario 2: premium blocked")
    print(
        "Expect: ToolAuthorisationMiddleware returns a ToolMessage; "
        "premium tool does not run.\n"
    )
    invoke_and_print("Create a 7 day study plan for Python decorators")

    print_section("Scenario 3: tool failure")
    print(
        "Expect: error middleware catches the failing tool and returns a safe "
        "ToolMessage.\n"
    )
    invoke_and_print("Use broken_quiz_generator for Python decorators")

    print_section("Scenario 4: long history (trimming)")
    long_conversation = [
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Message 3"},
        {"role": "assistant", "content": "Response 3"},
        {"role": "user", "content": "Explain Python decorators"},
    ]
    invoke_messages_and_print(long_conversation)

    print_section("What Changed?")
    print(
        "This capstone composes four production middleware layers:\n"
        "- Logging (visibility into lifecycle)\n"
        "- Message trimming (bounded context)\n"
        "- Tool authorisation (premium controls)\n"
        "- Error handling (safe tool failures)\n"
        "\nPart 05 is complete."
    )


if __name__ == "__main__":
    main()
