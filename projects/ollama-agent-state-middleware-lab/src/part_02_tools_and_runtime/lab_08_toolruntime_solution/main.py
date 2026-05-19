"""
Lab 08: ToolRuntime Solution

This lab demonstrates the framework-native ToolRuntime pattern - the correct
solution to Lab 07's manual state passing anti-pattern.

Key concepts:
- AgentState: Define structured state with type annotations
- @tool: Decorator that registers tools for the agent
- ToolRuntime: Framework-injected runtime (NOT a custom dataclass)
- Command(update={...}): Return value to update state atomically
- ToolMessage: Message to communicate tool results to the agent
- create_agent: Creates an agent with tools and state schema
- MemorySaver + thread_id: State persistence across invocations

Lab emphasis:
- Lab 06 = tools read/write state (basic pattern)
- Lab 07 = manual state passing challenge (anti-pattern to avoid)
- Lab 08 = ToolRuntime solution explained clearly (correct pattern with authorisation)

Developer notes:
- ToolRuntime is automatically injected by the framework (hidden from the LLM)
- authorised_tools in state controls which tools can execute
- Read tools return str; write tools return Command(update={...})
- ToolMessage is required in updates so the LLM knows tools ran
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


class RuntimeLearningState(AgentState):
    """State for runtime learning with authorisation tracking."""

    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int
    authorised_tools: list[str]


def create_initial_state() -> dict[str, Any]:
    """Create the initial state for the learning agent with authorised tools."""
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
        ],
        "current_topic": "toolruntime_solution",
        "last_action": "started_toolruntime_solution",
        "notes": [],
        "tool_call_count": 0,
        "authorised_tools": [
            "read_learning_status",
            "add_learning_note",
            "complete_topic",
        ],
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
            "notes": state.get("notes", []),
            "tool_call_count": state.get("tool_call_count", 0),
            "authorised_tools": state.get("authorised_tools", []),
        },
        indent=2,
    )


def invoke_agent(agent: Any, message: str, config: RunnableConfig) -> dict[str, Any]:
    """Invoke the agent with a user message and return the result."""
    result = {}
    for chunk in agent.stream(
        cast(Any, {"messages": [HumanMessage(content=message)]}),
        config=config,
        stream_mode="values",
    ):
        result = chunk
    return result


def is_tool_authorised(runtime: ToolRuntime, tool_name: str) -> bool:
    """Check if a tool is authorised to run based on state."""
    authorised_tools = runtime.state.get("authorised_tools", [])
    return tool_name in authorised_tools


@tool
def read_learning_status(runtime: ToolRuntime) -> str:
    """Read the current learning status from agent state."""
    tool_name = "read_learning_status"

    if not is_tool_authorised(runtime, tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return f"Tool blocked: {tool_name} not authorised"

    runtime.state["tool_call_count"] = runtime.state.get("tool_call_count", 0) + 1
    runtime.state["last_action"] = "tool_read_learning_status"

    state = runtime.state

    return (
        f"Learner: {state.get('learner_name', 'Unknown')}\n"
        f"Preferred language: {state.get('preferred_language', 'Unknown')}\n"
        f"Completed topics: {', '.join(state.get('completed_topics', []))}\n"
        f"Current topic: {state.get('current_topic', 'Unknown')}\n"
        f"Tool call count: {state.get('tool_call_count', 0)}\n"
        f"Authorised tools: {', '.join(state.get('authorised_tools', []))}"
    )


@tool
def add_learning_note(note: str, runtime: ToolRuntime) -> Command:
    """Add a note to the learning state."""
    tool_name = "add_learning_note"

    if not is_tool_authorised(runtime, tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name} not authorised",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    notes = runtime.state.get("notes", [])
    updated_notes = notes + [note]
    tool_call_count = runtime.state.get("tool_call_count", 0) + 1

    return Command(
        update={
            "notes": updated_notes,
            "tool_call_count": tool_call_count,
            "last_action": "tool_added_learning_note",
            "messages": [
                ToolMessage(
                    content=f"Note added: {note}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def complete_topic(topic: str, next_topic: str, runtime: ToolRuntime) -> Command:
    """Mark a topic as completed and advance to the next topic."""
    tool_name = "complete_topic"

    if not is_tool_authorised(runtime, tool_name):
        runtime.state["last_action"] = f"blocked_tool:{tool_name}"
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name} not authorised",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    completed_topics = runtime.state.get("completed_topics", [])
    updated_completed = (
        completed_topics + [topic]
        if topic not in completed_topics
        else completed_topics
    )
    tool_call_count = runtime.state.get("tool_call_count", 0) + 1

    return Command(
        update={
            "completed_topics": updated_completed,
            "current_topic": next_topic,
            "tool_call_count": tool_call_count,
            "last_action": "tool_completed_topic",
            "messages": [
                ToolMessage(
                    content=f"Completed topic: {topic}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def run_read_step(agent: Any, config: RunnableConfig) -> None:
    """Step 1: Demonstrate tool reads through runtime."""
    user_message = "Read my learning status."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 1: tool reads through runtime")
    print_turn("user", user_message)
    print_turn("expected tool", "read_learning_status")
    print_turn("state after", format_state_fields(state))


def run_write_note_step(agent: Any, config: RunnableConfig) -> None:
    """Step 2: Demonstrate tool writes through runtime."""
    user_message = "Add a note: ToolRuntime groups state and context."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 2: tool writes through runtime")
    print_turn("user", user_message)
    print_turn("expected tool", "add_learning_note")
    print_turn("state after", format_state_fields(state))


def run_complete_topic_step(agent: Any, config: RunnableConfig) -> None:
    """Step 3: Demonstrate tool updates progress through runtime."""
    user_message = "Complete the ToolRuntime solution lab and move to next topic."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 3: tool updates progress through runtime")
    print_turn("user", user_message)
    print_turn("expected tool", "complete_topic")
    print_turn("state after", format_state_fields(state))


def run_runtime_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 4: Show the runtime summary."""
    state = agent.get_state(config).values
    completed = state.get("completed_topics", [])
    current = state.get("current_topic", "Unknown")
    tool_count = state.get("tool_call_count", 0)
    last_action = state.get("last_action", "Unknown")

    summary = (
        f"Completed: {', '.join(completed)}\n"
        f"Current topic: {current}\n"
        f"Tool calls: {tool_count}\n"
        f"Last action: {last_action}"
    )

    print_section("Runtime summary")
    print_turn("summary", summary)
    print_turn("final state", format_state_fields(state))


def main() -> None:
    """Main entry point for Lab 08."""
    print_section("08 ToolRuntime Solution")

    model = get_chat_model()

    agent = create_agent(
        model=model,
        tools=[read_learning_status, add_learning_note, complete_topic],
        state_schema=RuntimeLearningState,
        checkpointer=MemorySaver(),
    )

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "toolruntime-solution-lab",
        }
    }

    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))

    run_read_step(agent, config)
    run_write_note_step(agent, config)
    run_complete_topic_step(agent, config)
    run_runtime_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "ToolRuntime is the framework-native solution to Lab 07's manual passing:\n"
        "- @tool decorator registers tools for the agent\n"
        "- ToolRuntime is injected by the framework (not manually created)\n"
        "- runtime.state reads current state, returns Command(update={...}) to write\n"
        "- ToolMessage is required so the LLM knows the tool ran\n"
        "- MemorySaver + thread_id persist state across invocations\n"
        "- authorised_tools in state controls tool access at runtime\n"
        "\nKey insight: This replaces the manual state-passing pattern from Lab 07."
    )


if __name__ == "__main__":
    main()