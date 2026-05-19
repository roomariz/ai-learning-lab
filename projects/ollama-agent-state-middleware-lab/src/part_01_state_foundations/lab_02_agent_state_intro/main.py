"""
Lab 02: Agent State Introduction

This lab demonstrates how to create a LangChain agent with structured state
using AgentState. Unlike a plain model call, agents can receive custom fields
alongside messages during a single agent invocation.

Key concepts:
- AgentState: A typed schema for agent state fields
- create_agent: Factory function that creates an agent with a state schema
- state_schema: Parameter that tells the agent what fields to expect in state

What you'll learn:
- How to define a custom state schema by subclassing AgentState
- How to create an agent that accepts structured state
- How to pass state into the agent via invoke()
"""

from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class PreferenceState(AgentState):
    """Custom state schema that includes a preferred_language field."""
    # In later labs, this field will be:
    # - Read by tools via ToolRuntime
    # - Updated via Command(update={...})
    # - Persisted later with a checkpointer
    preferred_language: str | None


def message_content_to_str(content: object) -> str:
    """Convert message content to string regardless of its type."""
    if isinstance(content, str):
        return content
    return str(content)


def main() -> None:
    print_section("02 Agent State Intro")

    model: ChatOllama = get_chat_model()

    # create_agent is a factory function that creates a LangChain agent.
    # It accepts:
    #   - model: The chat model to use (ChatOllama, ChatOpenAI, etc.)
    #   - tools: List of tools the agent can use (empty here for this intro)
    #   - state_schema: The state class that defines what fields the agent expects
    #
    # By passing state_schema=PreferenceState, we're telling the agent that
    # its state should include a 'preferred_language' field. This enables:
    # - Type checking: The agent knows what fields to expect
    # - Tool access: Tools can read/write these fields via ToolRuntime
    # - Persistence later: future labs will add checkpointers and thread IDs
    agent = create_agent(
        model=model,
        tools=[],
        state_schema=PreferenceState,
    )

    user_message = "What is my preferred programming language?"
    preferred_language = "Python"

    # The input state is a dictionary containing:
    #   - messages: List of messages to send to the model (required)
    #   - preferred_language: Our custom field from PreferenceState
    #
    # In this intro lab, we place the state value into the message so the model
    # can see it. Later labs will show tools reading state directly through
    # ToolRuntime, which is the preferred pattern for framework-based agents.
    input_state: dict[str, Any] = {
        "messages": [
            HumanMessage(
                content=(
                    f"Current state: preferred_language={preferred_language}\n\n"
                    f"User question: {user_message}"
                )
            ),
        ],
        "preferred_language": preferred_language,
    }

    # agent.invoke() runs the agent with the given input state. It takes the
    # input state (messages + custom fields), processes through the agent's
    # graph/nodes, and returns the output state with any updates.
    #
    # We use cast(Any, ...) because Pylance's generated type is narrower than
    # what LangChain actually accepts at runtime. LangChain accepts dicts with
    # the right keys; the cast satisfies the type checker while maintaining
    # correct runtime behaviour.
    result = agent.invoke(cast(Any, input_state))

    assistant_message = result["messages"][-1]

    print_section("Call with structured AgentState")
    print_turn("user", user_message)
    print_turn("state", "preferred_language=Python")
    print_turn("assistant", message_content_to_str(assistant_message.content))

    print_section("Conclusion")
    print(
        "This lab introduces LangChain AgentState. "
        "Unlike a plain model call, the agent can receive structured fields "
        "alongside messages during a single invocation. "
        "Later labs will show persistence, tools, ToolRuntime, "
        "Command(update={...}), and ToolMessage."
    )


if __name__ == "__main__":
    main()