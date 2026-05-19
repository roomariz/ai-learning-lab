"""
Lab 06: Tool State Read Write

This lab demonstrates how tools read from and write to agent state
using framework-native patterns.

Key concepts:
- AgentState: Define structured state with type annotations
- @tool: Decorator that registers tools for the agent
- ToolRuntime: Runtime object provided by the framework (injected automatically)
- Command(update={...}): Return value to update state atomically
- ToolMessage: Message to communicate tool results to the agent
- create_agent: Creates an agent with tools and state schema
- MemorySaver + thread_id: State persistence across invocations

This lab builds on Lab 05's persistence concepts by showing how
tools interact with state through framework mechanisms.

Developer notes:
- ToolRuntime is automatically injected by the framework (hidden from the LLM)
- read_learning_status returns str (read-only), others return Command(update={...}) (write)
- ToolMessage is required in the update so the LLM knows the tool ran
"""

import json
from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


def message_content_to_str(content: object) -> str:
    """Convert message content to string safely."""
    if isinstance(content, str):
        return content
    return str(content)


def message_to_str(message: object) -> str:
    """Convert a message object to string safely."""
    content = getattr(message, "content", message)
    return message_content_to_str(content)


# AgentState is the base class for custom state in LangGraph agents
# Define your state fields as class attributes with type annotations
# These fields persist across agent invocations when using a checkpointer
class LearningState(AgentState):
    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None
    notes: list[str]


def create_initial_state() -> dict[str, Any]:
    """Create the initial state for the learning agent."""
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": ["custom_state", "state_persistence"],
        "current_topic": "tool_state_read_write",
        "last_action": "started_tool_state_lab",
        "notes": [],
    }


def format_state_fields(state: dict[str, Any]) -> str:
    """Format state fields for display."""
    return json.dumps(
        {
            "learner_name": state.get("learner_name"),
            "preferred_language": state.get("preferred_language"),
            "completed_topics": state.get("completed_topics"),
            "current_topic": state.get("current_topic"),
            "last_action": state.get("last_action"),
            "notes": state.get("notes"),
        },
        indent=2,
    )


def invoke_agent(agent: Any, message: str, config: RunnableConfig) -> dict[str, Any]:
    """Invoke the agent with a user message and return the result.

    Uses stream mode to properly execute tools and update state.
    """
    result = {}
    for chunk in agent.stream(
        cast(Any, {"messages": [HumanMessage(content=message)]}),
        config=config,
        stream_mode="values",
    ):
        result = chunk
    return result


# READ TOOL: Uses runtime.state to read current agent state
# Returns str - the tool result is returned directly to the LLM
# The runtime parameter is HIDDEN from the LLM - it doesn't see it
@tool
def read_learning_status(runtime: ToolRuntime) -> str:
    """Read the current learning status from agent state."""
    # Access state via runtime.state - this is how tools read state
    state = runtime.state

    return (
        f"Learner: {state.get('learner_name', 'Unknown')}\n"
        f"Preferred language: {state.get('preferred_language', 'Unknown')}\n"
        f"Completed topics: {', '.join(state.get('completed_topics', []))}\n"
        f"Current topic: {state.get('current_topic', 'Unknown')}"
    )


# WRITE TOOL: Returns Command(update={...}) to modify agent state
# Command is the idiomatic way to mutate state in LangGraph
# ToolMessage is required so the LLM knows the tool ran successfully
@tool
def add_learning_note(note: str, runtime: ToolRuntime) -> Command:
    """Add a note to the learning state."""
    # Read current state
    notes = runtime.state.get("notes", [])
    updated_notes = notes + [note]

    # Return Command to update state - this is how tools write back to state
    # The framework applies these updates to the agent state atomically
    return Command(
        update={
            "notes": updated_notes,
            "last_action": "tool_added_learning_note",
            # ToolMessage is required so the LLM knows the tool ran successfully
            # The tool_call_id comes from runtime and identifies this tool call
            "messages": [
                ToolMessage(
                    content=f"Note added: {note}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# WRITE TOOL: Another example of a tool that updates state
@tool
def complete_topic(topic: str, runtime: ToolRuntime) -> Command:
    """Mark a topic as completed and advance to the next topic."""
    completed_topics = runtime.state.get("completed_topics", [])
    # Only add if not already in the list
    updated_completed = (
        completed_topics + [topic]
        if topic not in completed_topics
        else completed_topics
    )

    return Command(
        update={
            "completed_topics": updated_completed,
            "current_topic": "toolruntime_solution",
            "last_action": "tool_completed_topic",
            "messages": [
                ToolMessage(
                    content=f"Completed topic: {topic}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def run_read_tool_step(agent: Any, config: RunnableConfig) -> None:
    """Step 1: Demonstrate a tool that reads from state."""
    user_message = "Read my current learning status."

    result = invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values
    assistant_message = result["messages"][-1]

    print_section("Step 1: tool reads from state")
    print_turn("user", user_message)
    print_turn("expected tool", "read_learning_status")
    print_turn("assistant", message_to_str(assistant_message))
    print_turn("state accessed via", "runtime.state (injected by framework)")


def run_write_note_tool_step(agent: Any, config: RunnableConfig) -> None:
    """Step 2: Demonstrate a tool that writes to state."""
    user_message = "Add a note that tools can update structured state."

    result = invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values
    assistant_message = result["messages"][-1]

    print_section("Step 2: tool writes a note to state")
    print_turn("user", user_message)
    print_turn("expected tool", "add_learning_note")
    print_turn("assistant", message_to_str(assistant_message))
    print_turn("state after update", format_state_fields(state))
    print_turn("update mechanism", "Command(update={...})")

    if not state.get("notes"):
        print_turn(
            "warning",
            "Expected note was not added. The model may not have called the tool.",
    )

def run_complete_topic_tool_step(agent: Any, config: RunnableConfig) -> None:
    """Step 3: Demonstrate another tool that writes to state."""
    user_message = "Mark the tool state read/write lab as complete."

    result = invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values
    assistant_message = result["messages"][-1]

    print_section("Step 3: tool updates progress in state")
    print_turn("user", user_message)
    print_turn("expected tool", "complete_topic")
    print_turn("assistant", message_to_str(assistant_message))
    print_turn("state after update", format_state_fields(state))

    if state.get("last_action") != "tool_completed_topic":
        print_turn(
            "warning",
            "Expected topic completion did not occur. The model may not have called the tool.",
        )


def run_final_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 4: Show the deterministic summary of updated state."""
    user_message = "Summarise what changed after the tools ran."

    state = agent.get_state(config).values

    completed_topic = "tool_state_read_write"
    current_topic = state.get("current_topic", "Unknown")
    notes = state.get("notes", [])
    last_note = notes[-1] if notes else "No note was added."
    last_action = state.get("last_action", "Unknown")

    summary = (
        f"The tools added this note: {last_note}\n"
        f"The completed topic is now: {completed_topic}\n"
        f"The current topic is now: {current_topic}\n"
        f"The last action is now: {last_action}"
    )

    print_section("Step 4: deterministic summary of updated state")
    print_turn("user", user_message)
    print_turn("summary", summary)
    print_turn("final state", format_state_fields(state))


def main() -> None:
    """Main entry point for Lab 06."""
    print_section("06 Tool State Read Write")

    model = get_chat_model()

    # create_agent combines model, tools, state schema, and persistence
    # - model: The LLM that drives agent decisions
    # - tools: Functions the agent can call to read/write state
    # - state_schema: Typed fields that persist across invocations
    # - checkpointer: Storage backend for state (MemorySaver for dev)
    agent = create_agent(
        model=model,
        tools=[read_learning_status, add_learning_note, complete_topic],
        state_schema=LearningState,
        checkpointer=MemorySaver(),
    )

    # thread_id is the key that identifies this conversation session
    # Using the same thread_id across calls loads the persisted state automatically
    config: RunnableConfig = {
        "configurable": {
            "thread_id": "learning-state-tool-demo",
        }
    }

    # Seed the checkpointer with the starting state for this thread
    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))

    # Run the demonstration steps
    run_read_tool_step(agent, config)
    run_write_note_tool_step(agent, config)
    run_complete_topic_tool_step(agent, config)
    run_final_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "Tools read from and write to agent state using framework patterns:\n"
        "- @tool decorator registers tools for the agent\n"
        "- ToolRuntime is injected by the framework (not manually created)\n"
        "- runtime.state accesses current state\n"
        "- Command(update={...}) atomically updates state\n"
        "- ToolMessage communicates results back to the agent\n"
        "- MemorySaver and thread_id persist state across invocations\n"
        "\nKey insight: The runtime parameter is HIDDEN from the LLM.\n"
        "The framework automatically injects ToolRuntime when tools are called."
    )


if __name__ == "__main__":
    main()