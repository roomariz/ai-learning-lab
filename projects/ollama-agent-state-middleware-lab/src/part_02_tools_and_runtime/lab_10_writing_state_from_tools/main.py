"""
Lab 10: Writing State from Tools

This lab demonstrates writing state through Command(update={...}) in tools.
This is the counterpart to Lab 09 which was read-only.

Key concepts:
- AgentState: Define structured state with type annotations
- @tool: Decorator that registers tools for the agent
- ToolRuntime: Framework-injected runtime for state access
- Command(update={...}): Return value that writes to state
- ToolMessage: Appended to messages in Command to record tool invocations
- MemorySaver + thread_id: State persistence across invocations
- authorised_tools in state: Controls which tools can execute

This lab demonstrates write access. Tools return Command to update state.
Lab 09 focused on read-only access through runtime.state inspection.
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


class LearnerState(AgentState):
    """State for learner with write tools demonstration."""

    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int
    authorised_tools: list[str]


def create_initial_state() -> dict[str, Any]:
    """Create the initial state for the learning agent."""
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "preferred_language": "Python",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
            "toolruntime_solution",
            "reading_state_in_tools",
        ],
        "current_topic": "writing_state_from_tools",
        "last_action": "started_writing_state_lab",
        "notes": [
            "Reading tools should inspect state without mutating it.",
        ],
        "tool_call_count": 0,
        "authorised_tools": [
            "add_learning_note",
            "complete_topic",
            "set_next_topic",
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
    return tool_name in runtime.state.get("authorised_tools", [])


@tool
def add_learning_note(runtime: ToolRuntime, note: str) -> Command:
    """Add a learning note to state."""
    tool_name = "add_learning_note"

    if not is_tool_authorised(runtime, tool_name):
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    current_notes = list(runtime.state.get("notes", []))
    current_notes.append(note)
    current_tool_count = runtime.state.get("tool_call_count", 0)

    return Command(
        update={
            "notes": current_notes,
            "tool_call_count": current_tool_count + 1,
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
def complete_topic(runtime: ToolRuntime, topic: str, next_topic: str) -> Command:
    """Complete a topic and set the next topic."""
    tool_name = "complete_topic"

    if not is_tool_authorised(runtime, tool_name):
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    completed_topics = list(runtime.state.get("completed_topics", []))
    if topic not in completed_topics:
        completed_topics.append(topic)
    current_tool_count = runtime.state.get("tool_call_count", 0)

    return Command(
        update={
            "completed_topics": completed_topics,
            "current_topic": next_topic,
            "tool_call_count": current_tool_count + 1,
            "last_action": "tool_completed_topic",
            "messages": [
                ToolMessage(
                    content=f"Completed {topic}; next topic is {next_topic}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def set_next_topic(runtime: ToolRuntime, next_topic: str) -> Command:
    """Set the next topic without completing the current one."""
    tool_name = "set_next_topic"

    if not is_tool_authorised(runtime, tool_name):
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    current_tool_count = runtime.state.get("tool_call_count", 0)

    return Command(
        update={
            "current_topic": next_topic,
            "tool_call_count": current_tool_count + 1,
            "last_action": "tool_set_next_topic",
            "messages": [
                ToolMessage(
                    content=f"Current topic set to {next_topic}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def delete_all_notes(runtime: ToolRuntime) -> Command:
    """Delete all notes (admin operation)."""
    tool_name = "delete_all_notes"

    if not is_tool_authorised(runtime, tool_name):
        return Command(
            update={
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    current_tool_count = runtime.state.get("tool_call_count", 0)

    return Command(
        update={
            "notes": [],
            "tool_call_count": current_tool_count + 1,
            "last_action": "tool_deleted_all_notes",
            "messages": [
                ToolMessage(
                    content="All notes deleted.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def run_add_note_step(agent: Any, config: RunnableConfig) -> None:
    """Step 1: Add a learning note to state."""
    user_message = "Add a note about writing state from tools."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 1: tool writes a note")
    print_turn("user", user_message)
    print_turn("expected tool", "add_learning_note")
    print_turn("state after", format_state_fields(state))

    if len(state.get("notes", [])) > 1:
        print_turn("result", "Note was added to state successfully.")
    else:
        print_turn("warning", "Note should have been added to state.")


def run_complete_topic_step(agent: Any, config: RunnableConfig) -> None:
    """Step 2: Complete a topic and set the next."""
    user_message = "Complete the writing state from tools lab."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 2: tool completes topic")
    print_turn("user", user_message)
    print_turn("expected tool", "complete_topic")
    print_turn("state after", format_state_fields(state))

    completed = state.get("completed_topics", [])
    if "writing_state_from_tools" in completed:
        print_turn("result", "Topic was completed and next was set.")
    else:
        print_turn("warning", "Topic should have been completed.")


def run_set_next_topic_step(agent: Any, config: RunnableConfig) -> None:
    """Step 3: Set the next topic directly."""
    user_message = "Set the next topic to context versus state."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 3: tool sets next topic")
    print_turn("user", user_message)
    print_turn("expected tool", "set_next_topic")
    print_turn("state after", format_state_fields(state))

    if state.get("current_topic") == "context_vs_state":
        print_turn("result", "Current topic was updated.")
    else:
        print_turn("warning", "Current topic should have been updated.")


def run_blocked_write_step(agent: Any, config: RunnableConfig) -> None:
    """Step 4: Attempt an unauthorised write (should be blocked)."""
    user_message = "Try to delete all notes."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 4: unauthorised write is blocked")
    print_turn("user", user_message)
    print_turn("expected tool", "delete_all_notes")
    print_turn("state after", format_state_fields(state))

    if state.get("last_action") == "blocked_tool:delete_all_notes":
        print_turn("result", "Unauthorised tool was blocked.")
    else:
        print_turn("warning", "Unauthorised tool should have been blocked.")


def run_write_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 5: Show the write summary."""
    state = agent.get_state(config).values
    tool_count = state.get("tool_call_count", 0)

    summary = (
        "Writing state from tools changed the agent state in controlled ways:\n"
        f"Tool call count: {tool_count}\n"
        f"Completed topics: {len(state.get('completed_topics', []))}\n"
        f"Current topic: {state.get('current_topic')}\n"
        f"Last action: {state.get('last_action')}\n"
        f"Notes count: {len(state.get('notes', []))}"
    )

    print_section("Write summary")
    print_turn("summary", summary)
    print_turn("final state", format_state_fields(state))


def main() -> None:
    """Main entry point for Lab 10."""
    print_section("10 Writing State from Tools")

    model = get_chat_model()

    agent = create_agent(
        model=model,
        tools=[
            add_learning_note,
            complete_topic,
            set_next_topic,
            delete_all_notes,
        ],
        state_schema=LearnerState,
        checkpointer=MemorySaver(),
    )

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "writing-state-from-tools-lab",
        }
    }

    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))

    run_add_note_step(agent, config)
    run_complete_topic_step(agent, config)
    run_set_next_topic_step(agent, config)
    run_blocked_write_step(agent, config)
    run_write_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "Writing tools intentionally change state through Command(update={...}).\n"
        "This lab demonstrates write access to state:\n"
        "- @tool decorator registers tools for the agent\n"
        "- ToolRuntime is injected by the framework\n"
        "- Command(update={...}) returns updates to apply to state\n"
        "- ToolMessage records the tool invocation in messages\n"
        "- authorised_tools in state controls tool access at runtime\n"
        "- MemorySaver + thread_id persist state across invocations\n"
        "\nThe key pattern for writing state:\n"
        "    return Command(\n"
        "        update={\n"
        '            "field": new_value,\n'
        '            "messages": [ToolMessage(content="...", tool_call_id=runtime.tool_call_id)],\n'
        "        }\n"
        "    )\n"
        "\nWrite tools are useful for adding notes, completing tasks, setting state, and persisting results.\n"
        "\nLab 09 was read-only; Lab 10 is write-focused."
    )


if __name__ == "__main__":
    main()