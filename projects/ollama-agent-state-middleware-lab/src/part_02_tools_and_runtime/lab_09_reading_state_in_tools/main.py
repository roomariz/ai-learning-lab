"""
Lab 09: Reading State in Tools

This lab demonstrates reading state through ToolRuntime without modifying domain state.
This is the foundation before learning to write state (Lab 10).

Key concepts:
- AgentState: Define structured state with type annotations
- @tool: Decorator that registers tools for the agent
- ToolRuntime: Framework-injected runtime for state access
- runtime.state: Read current state (tools return str, not Command)
- MemorySaver + thread_id: State persistence across invocations
- authorised_tools in state: Controls which tools can execute

This lab demonstrates read-only access. No domain state fields are updated by these tools.
Tools may inspect runtime.state, but they must not mutate it via Command.
Lab 10 focuses on state writes through Command(update={...}).
"""

import json
from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


class LearnerState(AgentState):
    """State for learner with read-only tools demonstration."""

    learner_name: str
    preferred_language: str
    completed_topics: list[str]
    current_topic: str
    last_action: str
    notes: list[str]
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
        ],
        "current_topic": "reading_state_in_tools",
        "last_action": "started_reading_state_lab",
        "notes": [
            "ToolRuntime groups state and context behind one clean tool interface."
        ],
        "authorised_tools": [
            "read_profile",
            "read_progress",
            "read_next_topic",
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
def read_profile(runtime: ToolRuntime) -> str:
    """Read the learner's profile from state."""
    tool_name = "read_profile"

    if not is_tool_authorised(runtime, tool_name):
        return f"Tool blocked: {tool_name} not authorised"

    return (
        f"Learner: {runtime.state.get('learner_name', 'Unknown')}\n"
        f"Preferred language: {runtime.state.get('preferred_language', 'Unknown')}\n"
        f"Role: learner"
    )


@tool
def read_progress(runtime: ToolRuntime) -> str:
    """Read the learner's progress from state."""
    tool_name = "read_progress"

    if not is_tool_authorised(runtime, tool_name):
        return f"Tool blocked: {tool_name} not authorised"

    completed_topics = runtime.state.get("completed_topics", [])
    completed_list = "\n".join(f"- {topic}" for topic in completed_topics)
    last_action = runtime.state.get("last_action", "None")

    return (
        "Completed topics:\n"
        f"{completed_list}\n"
        f"Last action: {last_action}"
    )


@tool
def read_next_topic(runtime: ToolRuntime) -> str:
    """Read the learner's current topic from state."""
    tool_name = "read_next_topic"

    if not is_tool_authorised(runtime, tool_name):
        return f"Tool blocked: {tool_name} not authorised"

    return f"Current topic: {runtime.state.get('current_topic', 'Unknown')}"


@tool
def attempt_unauthorised_read(runtime: ToolRuntime) -> str:
    """Attempt to read private admin notes (should be blocked)."""
    tool_name = "read_private_admin_notes"

    if not is_tool_authorised(runtime, tool_name):
        return f"Tool blocked: {tool_name} not authorised"

    return "This should not be visible."


def run_profile_read_step(agent: Any, config: RunnableConfig) -> None:
    """Step 1: Read learner profile from state."""
    user_message = "Read my learner profile from state."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 1: tool reads learner profile")
    print_turn("user", user_message)
    print_turn("expected tool", "read_profile")
    print_turn("state after", format_state_fields(state))

    if state.get("last_action") != "started_reading_state_lab":
        print_turn("warning", "A read-only tool should not update domain state.")


def run_progress_read_step(agent: Any, config: RunnableConfig) -> None:
    """Step 2: Read learning progress from state."""
    user_message = "Read my completed topics from state."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 2: tool reads learning progress")
    print_turn("user", user_message)
    print_turn("expected tool", "read_progress")
    print_turn("state after", format_state_fields(state))

    if state.get("last_action") != "started_reading_state_lab":
        print_turn("warning", "A read-only tool should not update domain state.")


def run_next_topic_read_step(agent: Any, config: RunnableConfig) -> None:
    """Step 3: Read current topic from state."""
    user_message = "Read my current topic from state."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 3: tool reads current topic")
    print_turn("user", user_message)
    print_turn("expected tool", "read_next_topic")
    print_turn("state after", format_state_fields(state))

    if state.get("last_action") != "started_reading_state_lab":
        print_turn("warning", "A read-only tool should not update domain state.")


def run_blocked_read_step(agent: Any, config: RunnableConfig) -> None:
    """Step 4: Attempt to read private admin notes (should be blocked)."""
    user_message = "Try to read private admin notes."
    invoke_agent(agent, user_message, config)
    state = agent.get_state(config).values

    print_section("Step 4: unauthorised read is blocked")
    print_turn("user", user_message)
    print_turn("expected tool", "attempt_unauthorised_read")
    print_turn("state after", format_state_fields(state))

    if state.get("last_action") != "started_reading_state_lab":
        print_turn("warning", "A read-only tool should not update domain state.")


def run_read_only_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 5: Show the read-only summary."""
    state = agent.get_state(config).values
    current_topic = state.get("current_topic", "Unknown")
    last_action = state.get("last_action", "Unknown")

    summary = (
        "Reading state in tools is useful when a tool needs current facts before acting.\n"
        "This lab only reads state. It does not update state.\n"
        f"Current topic remains: {current_topic}\n"
        f"Last action remains: {last_action}"
    )

    print_section("Read-only summary")
    print_turn("summary", summary)
    print_turn("final state", format_state_fields(state))


def main() -> None:
    """Main entry point for Lab 09."""
    print_section("09 Reading State in Tools")

    model = get_chat_model()

    agent = create_agent(
        model=model,
        tools=[
            read_profile,
            read_progress,
            read_next_topic,
            attempt_unauthorised_read,
        ],
        state_schema=LearnerState,
        checkpointer=MemorySaver(),
    )

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "reading-state-in-tools-lab",
        }
    }

    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))

    run_profile_read_step(agent, config)
    run_progress_read_step(agent, config)
    run_next_topic_read_step(agent, config)
    run_blocked_read_step(agent, config)
    run_read_only_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "Tools can read state to make informed decisions without changing it.\n"
        "This lab demonstrates read-only access to state through ToolRuntime:\n"
        "- @tool decorator registers tools for the agent\n"
        "- ToolRuntime is injected by the framework\n"
        "- runtime.state reads current state (no writes in this lab)\n"
        "- authorised_tools in state controls tool access at runtime\n"
        "- MemorySaver + thread_id persist state across invocations\n"
        "\nRead-only tools are useful for profile checks, progress checks, permission checks, and routing decisions.\n"
        "\nLab 10 will cover writing state through Command(update={...})."
    )


if __name__ == "__main__":
    main()