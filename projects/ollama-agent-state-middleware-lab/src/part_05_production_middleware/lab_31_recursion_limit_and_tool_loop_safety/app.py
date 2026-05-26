"""
Lab 31: Recursion Limit and Tool Loop Safety

Purpose: Protect production agents from runaway tool-calling loops.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.part_05_production_middleware.lab_22_tool_authorisation_middleware.middleware import (
    ToolLoopGuardMiddleware,
)
from src.part_05_production_middleware.lab_31_recursion_limit_and_tool_loop_safety.middleware import (
    ToolCallLimitMiddleware,
)
from src.part_05_production_middleware.lab_31_recursion_limit_and_tool_loop_safety.tools import (
    _loop_counter,
    looping_tool,
)

model = get_chat_model()

normal_agent = create_agent(
    model=model,
    tools=[looping_tool],
    middleware=[],
)

protected_agent = create_agent(
    model=model,
    tools=[looping_tool],
    middleware=[
        ToolCallLimitMiddleware(max_tool_calls=3),
        ToolLoopGuardMiddleware(max_same_tool_calls=2),
    ],
)


def invoke_and_print(agent, prompt: str) -> None:
    print_turn("user", prompt)

    try:
        response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    except Exception as exc:
        print_turn("assistant", f"Stopped safely: {exc}")
        print()
        return

    for message in response["messages"]:
        role = getattr(message, "type", "unknown")
        content = getattr(message, "content", "")
        if role == "tool" and content:
            print_turn("tool", content)

    final_message = response["messages"][-1]
    print_turn("assistant", final_message.content)
    print()


def main() -> None:
    prompt = (
        "Call looping_tool repeatedly. After each result, call it again. "
        "Do not stop unless you are forced to by a safety limit."
    )

    print_section("31 Recursion Limit and Tool Loop Safety")

    _loop_counter.reset()
    print_section("Normal agent (no safety)")
    print(
        "This case is not executed because it may loop indefinitely.\n"
        "Without recursion limits or loop guards, the model can keep calling the same tool."
    )

    _loop_counter.reset()
    print_section("Protected agent (safe stop)")
    print("Expect: tool-loop guard and/or tool-call limit blocks further tool calls.\n")
    invoke_and_print(protected_agent, prompt)


if __name__ == "__main__":
    main()

