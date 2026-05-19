"""
Lab 11: Context vs State

This lab demonstrates the distinction between:
- State (AgentState): Mutable data that changes during a conversation
- Context: Stable run metadata that stays constant throughout a run

Key concepts:
- AgentState: Mutable fields that change over time (learner_name, notes, tool_call_count)
- RUN_CONTEXT: Immutable config that seeds the prompt and stays constant
- runtime.state: Access to mutable state in tools
- Concept: state = changing data, context = stable run metadata

This lab does NOT use:
- Custom Runtime dataclass (not framework-native)
- TypedDict for state (use AgentState instead)
- Direct state mutation (use Command(update={...}))
- Pretend context is auto-injected (context is separate dictionary)

Lab 09: read state
Lab 10: write state
Lab 11: distinguish mutable state from stable context
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


class ContextState(AgentState):
    """State for context vs state demonstration.

    These fields are MUTABLE - they change during the conversation.
    """

    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
    tool_call_count: int
    authorised_tools: list[str]


# Stable context that does not change during the run.
# This represents run metadata such as user_id, role, tenant_id, and environment.
# It is separate from AgentState and is not automatically injected into runtime.state.
RUN_CONTEXT = {
    "user_id": "learner-001",
    "role": "learner",
    "tenant_id": "learning-lab",
    "environment": "local",
}


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
            "writing_state_from_tools",
        ],
        "current_topic": "context_vs_state",
        "last_action": "started_context_vs_state_lab",
        "notes": [
            "State changes during conversation; context is stable.",
        ],
        "tool_call_count": 0,
        "authorised_tools": [
            "add_learning_note",
            "complete_topic",
            "show_context_info",
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


def format_context_info() -> str:
    """Format context for display."""
    return json.dumps(RUN_CONTEXT, indent=2)


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


# This tool reads stable context but still updates state metadata.
# tool_call_count and last_action are mutable execution state.
@tool
def show_context_info(runtime: ToolRuntime) -> Command:
    """Show the stable context information.

    This tool demonstrates that context is separate from state.
    Context is passed as a constant dictionary, not in runtime.state.
    """
    tool_name = "show_context_info"

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

    context_summary = (
        f"Context (stable): {RUN_CONTEXT}\n"
        f"State (mutable) - learner: {runtime.state.get('learner_name')}, "
        f"topic: {runtime.state.get('current_topic')}, "
        f"notes: {len(runtime.state.get('notes', []))}"
    )

    return Command(
        update={
            "tool_call_count": current_tool_count + 1,
            "last_action": "tool_showed_context_info",
            "messages": [
                ToolMessage(
                    content=context_summary,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def run_add_note_step(agent: Any, config: RunnableConfig) -> None:
    """Step 1: Add a learning note to state."""
    user_message = "Add a note about distinguishing context from state."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 1: tool adds a note (state changes)")
    print_turn("user", user_message)
    print_turn("context (unchanged)", format_context_info())
    print_turn("state after", format_state_fields(state))

    if len(state.get("notes", [])) > 1:
        print_turn("result", "Note was added - STATE changed.")
    else:
        print_turn("warning", "Note should have been added to state.")


def run_complete_topic_step(agent: Any, config: RunnableConfig) -> None:
    """Step 2: Complete a topic."""
    user_message = "Complete the context vs state lab."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 2: tool completes topic (state changes)")
    print_turn("user", user_message)
    print_turn("context (unchanged)", format_context_info())
    print_turn("state after", format_state_fields(state))

    completed = state.get("completed_topics", [])
    if "context_vs_state" in completed:
        print_turn("result", "Topic was completed - STATE changed.")
    else:
        print_turn("warning", "Topic should have been completed.")


def run_show_context_step(agent: Any, config: RunnableConfig) -> None:
    """Step 3: Show context info."""
    user_message = "Show me the context information."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 3: tool shows context (state + context displayed)")
    print_turn("user", user_message)
    print_turn("context (stable)", format_context_info())
    print_turn("state after", format_state_fields(state))

    if "context_info" in state.get("last_action", ""):
        print_turn("result", "Context was shown - context stays constant.")
    else:
        print_turn("warning", "Context should have been shown.")


def run_context_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 4: Show the context vs state summary."""
    state = agent.get_state(config).values
    tool_count = state.get("tool_call_count", 0)

    summary = (
        "Context vs State distinction:\n"
        "CONTEXT (stable, constant):\n"
        f"  {RUN_CONTEXT}\n\n"
        "STATE (mutable, changes):\n"
        f"  learner_name: {state.get('learner_name')}\n"
        f"  current_topic: {state.get('current_topic')}\n"
        f"  tool_call_count: {tool_count}\n"
        f"  notes: {len(state.get('notes', []))}\n"
        f"  completed_topics: {len(state.get('completed_topics', []))}"
    )

    print_section("Context vs State Summary")
    print_turn("context (unchanged)", format_context_info())
    print_turn("state (changed)", format_state_fields(state))
    print_turn("explanation", summary)


def main() -> None:
    """Main entry point for Lab 11."""
    print_section("11 Context vs State")

    model = get_chat_model()

    agent = create_agent(
        model=model,
        tools=[
            add_learning_note,
            complete_topic,
            show_context_info,
        ],
        state_schema=ContextState,
        checkpointer=MemorySaver(),
    )

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "context-vs-state-lab",
        }
    }

    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))
    print_turn("run context (constant)", format_context_info())

    run_add_note_step(agent, config)
    run_complete_topic_step(agent, config)
    run_show_context_step(agent, config)
    run_context_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "Context vs State distinction:\n"
        "\n"
        "STATE (AgentState) - Mutable:\n"
        "- Changes during conversation\n"
        "- Fields: learner_name, notes, current_topic, tool_call_count\n"
        "- Tools modify via Command(update={...})\n"
        "- Access via runtime.state in tools\n"
        "\n"
        "CONTEXT (RUN_CONTEXT) - Stable:\n"
        "- Constant throughout the run\n"
        "- Fields: user_id, role, tenant_id, environment\n"
        "- Passed separately to seed prompts\n"
        "- Not automatically in runtime.state\n"
        "\n"
        "Key insight:\n"
        "  state = changing data (in AgentState)\n"
        "  context = stable run metadata (separate dict)\n"
        "\n"
        "Lab 09: read state\n"
        "Lab 10: write state\n"
        "Lab 11: distinguish mutable state from stable context"
    )


if __name__ == "__main__":
    main()