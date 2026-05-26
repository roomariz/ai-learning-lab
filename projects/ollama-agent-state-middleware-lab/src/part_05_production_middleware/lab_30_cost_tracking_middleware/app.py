"""
Lab 30: Cost Tracking Middleware

Purpose: Track estimated model/tool usage so production agents do not run
invisibly or expensively.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_30_cost_tracking_middleware.middleware import (
    CostTrackingMiddleware,
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
        CostTrackingMiddleware(),
    ],
)


def invoke_and_print(prompt: str) -> None:
    print_turn("user", prompt)
    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    final_message = response["messages"][-1]
    print_turn("assistant", final_message.content)
    print()


def main() -> None:
    print_section("30 Cost Tracking Middleware")
    print(
        "Goal: visibility into rough local cost signals.\n"
        "Logs: request started, message count, tool call count, estimated cost.\n"
    )

    invoke_and_print(
        "Explain Python decorators using explain_topic, then create a 3-day study "
        "plan using create_study_plan."
    )


if __name__ == "__main__":
    main()

