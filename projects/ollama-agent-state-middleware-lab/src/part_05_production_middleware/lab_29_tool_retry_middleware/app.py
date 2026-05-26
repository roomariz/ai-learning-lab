"""
Lab 29: Tool Retry Middleware

Purpose: Retry temporary tool failures before returning a safe error.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_29_tool_retry_middleware.middleware import (
    ToolRetryMiddleware,
)
from src.part_05_production_middleware.lab_29_tool_retry_middleware.tools import (
    _flaky_counter,
    flaky_tool,
)

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[flaky_tool],
    middleware=[ToolRetryMiddleware(max_attempts=3)],
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
    _flaky_counter.reset()

    print_section("29 Tool Retry Middleware")
    print(
        "Goal: recover from transient tool failures.\n"
        "Demo tool: fails twice, succeeds on third attempt.\n"
        "Middleware: retries before returning a safe error.\n"
    )

    invoke_and_print(
        "Call flaky_tool now and return its result. Do not do anything else."
    )


if __name__ == "__main__":
    main()

