"""
Lab 03: Custom State

This lab extends the simple AgentState pattern from Lab 02 into a richer
custom state schema with multiple structured fields.

It shows how an agent can receive profile, progress, current topic, and
last-action data alongside messages during a single invocation.
"""

from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class LearningState(AgentState):
    """Custom state schema with fields for learner profile and progress."""

    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None


def message_content_to_str(content: object) -> str:
    """Extract string content from a message, handling various formats."""
    if isinstance(content, str):
        return content
    return str(content)


def create_initial_state() -> dict[str, Any]:
    """Create the initial state with sample learner data."""
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": ["agent_state_intro"],
        "current_topic": "custom_state",
        "last_action": "updated_learning_profile",
    }


def format_state_summary(state: dict[str, Any]) -> str:
    """Format the state fields as a readable string for the prompt."""
    return (
        f"learner_name={state['learner_name']}\n"
        f"preferred_language={state['preferred_language']}\n"
        f"completed_topics={state['completed_topics']}\n"
        f"current_topic={state['current_topic']}\n"
        f"last_action={state['last_action']}"
    )


def main() -> None:
    print_section("03 Custom State")

    model: ChatOllama = get_chat_model()

    # Create an agent with the custom LearningState schema
    agent = create_agent(
        model=model,
        tools=[],
        state_schema=LearningState,
    )

    state = create_initial_state()
    user_message = "Summarise my current learning status."
    state_summary = format_state_summary(state)

    # Developer note:
    # **state unpacks every key/value pair from the existing state dictionary
    # into this new input dictionary.
    #
    # This avoids repeating each state field manually, for example:
    # learner_name=state["learner_name"],
    # preferred_language=state["preferred_language"],
    #
    # The "messages" key is then added for this specific agent invocation.
    # This keeps the structured state and the current user message together.
    input_state = {
        **state,
        "messages": [
            HumanMessage(
                content=(
                    f"Current custom agent state:\n{state_summary}\n\n"
                    f"User question: {user_message}"
                )
            )
        ],
    }

    result = agent.invoke(cast(Any, input_state))
    assistant_message = result["messages"][-1]

    print_section("Call with richer custom AgentState")
    print_turn("user", user_message)
    print_turn("state", state_summary)
    print_turn("assistant", message_content_to_str(assistant_message.content))

    print_section("Conclusion")
    print(
        "Custom AgentState lets the agent receive several structured fields "
        "alongside messages. This is more useful than passing one isolated "
        "value because it can carry profile, progress, current topic, and "
        "last action in one schema."
    )


if __name__ == "__main__":
    main()