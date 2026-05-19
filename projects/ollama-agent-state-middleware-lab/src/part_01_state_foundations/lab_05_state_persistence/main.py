"""
Lab 05: State Persistence

This lab shows how to persist structured AgentState across agent invocations
using MemorySaver and a stable thread_id.

It builds on Lab 03 by keeping custom state available beyond a single
invocation, without relying on message history.
"""

from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class PersistentLearningState(AgentState):
    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None


def message_content_to_str(content: object) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def create_initial_state() -> dict[str, Any]:
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": ["agent_state_intro", "custom_state"],
        "current_topic": "state_persistence",
        "last_action": "initialised_persistent_state",
    }


def format_state_summary(state: dict[str, Any]) -> str:
    return (
        f"learner_name={state['learner_name']}\n"
        f"preferred_language={state['preferred_language']}\n"
        f"completed_topics={state['completed_topics']}\n"
        f"current_topic={state['current_topic']}\n"
        f"last_action={state['last_action']}"
    )


def main() -> None:
    print_section("05 State Persistence")

    model: ChatOllama = get_chat_model()

    # checkpointer=MemorySaver() enables state persistence across invocations.
    # The agent now can reload structured state automatically on later calls.
    agent = create_agent(
        model=model,
        tools=[],
        state_schema=PersistentLearningState,
        checkpointer=MemorySaver(),
    )

    # thread_id is the key that identifies this conversation session.
    # Using the same thread_id across calls loads the persisted state automatically.
    config: RunnableConfig = {
        "configurable": {
            "thread_id": "learning-state-demo",
        }
    }

    initial_state = create_initial_state()
    # Seed the checkpointer with the starting state for this thread.
    # Later calls using the same config can retrieve this state.
    agent.update_state(config, initial_state)

    first_message = "Summarise my persisted learning state."
    first_state = agent.get_state(config).values
    first_summary = format_state_summary(first_state)

    first_input = {
        "messages": [
            HumanMessage(
                content=(
                    f"Current persisted state:\n{first_summary}\n\n"
                    f"User question: {first_message}"
                )
            )
        ]
    }

    first_result = agent.invoke(cast(Any, first_input), config=config)
    first_response = first_result["messages"][-1]

    print_section("Step 1: state saved under thread_id")
    print_turn("thread_id", "learning-state-demo")
    print_turn("user", first_message)
    print_turn("state", first_summary)
    print_turn("assistant", message_content_to_str(first_response.content))

    second_message = "What learning state do you still remember?"
    second_state = agent.get_state(config).values
    second_summary = format_state_summary(second_state)

    second_input = {
        "messages": [
            HumanMessage(
                content=(
                    f"Loaded state from same thread_id:\n{second_summary}\n\n"
                    f"User question: {second_message}"
                )
            )
        ]
    }

    second_result = agent.invoke(cast(Any, second_input), config=config)
    second_response = second_result["messages"][-1]

    print_section("Step 2: state loaded from same thread_id")
    print_turn("thread_id", "learning-state-demo")
    print_turn("user", second_message)
    print_turn("state", second_summary)
    print_turn("assistant", message_content_to_str(second_response.content))

    print_section("Conclusion")
    print(
        "State persistence uses a checkpointer and a stable thread_id. "
        "The checkpointer stores the agent state between invocations, so later "
        "calls can retrieve structured state without relying on message history."
    )


if __name__ == "__main__":
    main()