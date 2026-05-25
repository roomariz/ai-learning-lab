"""
Lab 27: Interactive Production Learning Agent

Purpose: Try the complete production learning agent in an interactive terminal chat.
"""

from langchain.agents import create_agent

from src.common.model import get_chat_model
from src.common.printer import print_section
from src.part_05_production_middleware.lab_26_complete_production_learning_agent.middleware import (
    production_middleware,
)
from src.part_05_production_middleware.lab_23_error_handling_middleware.tools import (
    broken_quiz_generator,
)
from src.part_05_production_middleware.shared.tools import (
    create_study_plan,
    explain_topic,
)

model = get_chat_model()

production_agent = create_agent(
    model=model,
    tools=[
        explain_topic,
        create_study_plan,
        broken_quiz_generator,
    ],
    middleware=production_middleware(),
)


def chat_with_agent() -> None:
    print_section("27 Interactive Guided Production Learning Agent")
    print("Choose a demo:")
    print("1. Explain Python decorators")
    print("2. Try premium study plan")
    print("3. Trigger broken quiz tool")
    print("q. Quit")

    prompts = {
        "1": "Explain Python decorators",
        "2": "Create a 7 day study plan for Python decorators",
        "3": "Use broken_quiz_generator for Python decorators",
    }

    while True:
        choice = input("Choose: ").strip().lower().rstrip(".")

        if choice in {"q", "quit", "exit"}:
            print("Goodbye!")
            break

        prompt = prompts.get(choice)

        if prompt is None:
            print("Please choose 1, 2, 3, or q.\n")
            continue

        response = production_agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )

        final_message = response["messages"][-1]
        print(f"\nAgent: {final_message.content}\n")

def main() -> None:
    chat_with_agent()



if __name__ == "__main__":
    main()

