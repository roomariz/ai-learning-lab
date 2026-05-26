"""
Lab 28: Rate Limiting Middleware

Purpose: Limit how many tool calls an agent can make in one request.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_28_rate_limiting_middleware.middleware import (
    RateLimitingMiddleware,
)
from src.part_05_production_middleware.shared.tools import create_study_plan, explain_topic

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[
        explain_topic,
        create_study_plan,
    ],
    middleware=[
        RateLimitingMiddleware(max_tool_calls=1),
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
    print_section("28 Rate Limiting Middleware")
    print(
        "Goal: limit tool calls per request.\n"
        "Config: max_tool_calls=1\n"
        "Expect: first tool call allowed, second tool call blocked.\n"
    )

    invoke_and_print(
        "Explain Python decorators using explain_topic, then create a 7-day study "
        "plan using create_study_plan."
    )


if __name__ == "__main__":
    main()

