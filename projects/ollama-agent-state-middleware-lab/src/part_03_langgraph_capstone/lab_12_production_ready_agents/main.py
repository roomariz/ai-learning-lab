"""
Lab 12: Production-Ready Agents

This lab demonstrates production controls around framework-native LangGraph agents.

Key concepts:
- AgentState: Define structured state with type annotations
- create_agent: Creates an agent with tools and state schema
- @tool: Decorator that registers tools for the agent
- ToolRuntime: Framework-injected runtime for state access
- Command(update={...}): Return value to update state atomically
- ToolMessage: Message to communicate tool results to the agent
- MemorySaver + thread_id: State persistence across invocations
- RunnableConfig: Configuration for agent invocation

Production controls added:
- Input validation before invoking the agent (deterministic, not prompt-only)
- Tool authorisation inside tools (checked at runtime)
- blocked_request_count in state (observability)
- error_count in state (observability)
- tool_call_count in state (observability)
- Deterministic summary at the end

Lab sequence:
- Lab 09 = read state
- Lab 10 = write state
- Lab 11 = context vs state
- Lab 12 = production controls around framework-native agents
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


class ProductionState(AgentState):
    """State for production-ready agents with observability fields."""

    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    tool_call_count: int
    blocked_request_count: int
    error_count: int
    authorised_tools: list[str]


def create_initial_state() -> dict[str, Any]:
    """Create the initial state for the production agent."""
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "current_topic": "production_ready_agents",
        "completed_topics": [
            "custom_state",
            "state_persistence",
            "tool_state_read_write",
            "toolruntime_solution",
            "reading_state_in_tools",
            "writing_state_from_tools",
            "context_vs_state",
        ],
        "last_action": "started_production_ready_agents_lab",
        "notes": [],
        "tool_call_count": 0,
        "blocked_request_count": 0,
        "error_count": 0,
        "authorised_tools": [
            "add_learning_note",
            "complete_topic",
        ],
    }


def format_state_fields(state: dict[str, Any]) -> str:
    """Format state fields for display."""
    return json.dumps(
        {
            "learner_name": state.get("learner_name"),
            "current_topic": state.get("current_topic"),
            "completed_topics": state.get("completed_topics"),
            "last_action": state.get("last_action"),
            "notes": state.get("notes", []),
            "tool_call_count": state.get("tool_call_count", 0),
            "blocked_request_count": state.get("blocked_request_count", 0),
            "error_count": state.get("error_count", 0),
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


def latest_message_to_str(state: dict[str, Any]) -> str:
    """Extract the latest message content as a string."""
    messages = state.get("messages", [])
    if not messages:
        return "No response"

    latest_message = messages[-1]
    content = getattr(latest_message, "content", latest_message)
    return content if isinstance(content, str) else str(content)


# Production control:
# Input validation happens before the agent is invoked.
# This keeps basic safety checks deterministic instead of relying on prompts.
def validate_input(user_input: str, max_input_length: int) -> str | None:
    """Validate input before agent invocation. Returns error message if blocked."""
    if not user_input.strip():
        return "Input blocked: message is empty."

    if len(user_input) > max_input_length:
        return f"Input blocked: message is too long (max {max_input_length} chars)."

    return None


def is_tool_authorised(runtime: ToolRuntime, tool_name: str) -> bool:
    """Check if a tool is authorised to run based on state."""
    return tool_name in runtime.state.get("authorised_tools", [])


@tool
def add_learning_note(note: str, runtime: ToolRuntime) -> Command:
    """Add a note to the learning state."""
    tool_name = "add_learning_note"

    if not is_tool_authorised(runtime, tool_name):
        blocked_count = runtime.state.get("blocked_request_count", 0)
        return Command(
            update={
                "blocked_request_count": blocked_count + 1,
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
        blocked_count = runtime.state.get("blocked_request_count", 0)
        return Command(
            update={
                "blocked_request_count": blocked_count + 1,
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


@tool
def risky_tool(runtime: ToolRuntime) -> Command:
    """Simulate a risky production tool that should be blocked."""
    tool_name = "risky_tool"

    if not is_tool_authorised(runtime, tool_name):
        blocked_count = runtime.state.get("blocked_request_count", 0)
        return Command(
            update={
                "blocked_request_count": blocked_count + 1,
                "last_action": f"blocked_tool:{tool_name}",
                "messages": [
                    ToolMessage(
                        content=f"Tool blocked: {tool_name} not authorised",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    error_count = runtime.state.get("error_count", 0)
    return Command(
        update={
            "error_count": error_count + 1,
            "last_action": "tool_error:risky_tool",
            "messages": [
                ToolMessage(
                    content="Tool failed safely: risky_tool",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def run_valid_request_step(
    agent: Any, config: RunnableConfig, max_input_length: int
) -> None:
    """Step 1: valid request is processed through the agent."""
    user_message = (
        "Add this note: Production agents need validation, authorisation, "
        "error handling, and observability."
    )

    validation_error = validate_input(user_message, max_input_length)

    if validation_error is not None:
        state = agent.get_state(config).values
        blocked_count = state.get("blocked_request_count", 0)
        agent.update_state(
            config,
            {
                "blocked_request_count": blocked_count + 1,
                "last_action": "blocked_input_validation",
            },
        )
        result = validation_error
    else:
        invoke_agent(agent, user_message, config)
        state = agent.get_state(config).values
        result = latest_message_to_str(state)

    print_section("Step 1: valid request is processed")
    print_turn("user", user_message)
    print_turn("result", result)

    state = agent.get_state(config).values
    print_turn("state", format_state_fields(state))

    if not state.get("notes"):
        print_turn(
            "warning",
            "Expected note was not added. The model may not have called the tool.",
        )


def run_invalid_input_step(
    agent: Any, config: RunnableConfig, max_input_length: int
) -> None:
    """Step 2: invalid input is blocked before agent invocation."""
    user_message = ""

    validation_error = validate_input(user_message, max_input_length)

    if validation_error is not None:
        state = agent.get_state(config).values
        blocked_count = state.get("blocked_request_count", 0)
        agent.update_state(
            config,
            {
                "blocked_request_count": blocked_count + 1,
                "last_action": "blocked_empty_input",
            },
        )
        result = validation_error
    else:
        result = "Input accepted."

    print_section("Step 2: invalid input is blocked")
    print_turn("user", "<empty message>")
    print_turn("result", result)

    state = agent.get_state(config).values
    print_turn("state", format_state_fields(state))


def run_unauthorised_tool_step(
    agent: Any, config: RunnableConfig, max_input_length: int
) -> None:
    """Step 3: unauthorised tool is blocked by tool-level authorisation."""
    user_message = "Run the risky production tool."

    validation_error = validate_input(user_message, max_input_length)

    if validation_error is not None:
        state = agent.get_state(config).values
        blocked_count = state.get("blocked_request_count", 0)
        agent.update_state(
            config,
            {
                "blocked_request_count": blocked_count + 1,
                "last_action": "blocked_input_validation",
            },
        )
        result = validation_error
    else:
        invoke_agent(agent, user_message, config)
        state = agent.get_state(config).values
        result = latest_message_to_str(state)

    print_section("Step 3: unauthorised tool is blocked")
    print_turn("user", user_message)
    print_turn("result", result)

    state = agent.get_state(config).values
    print_turn("state", format_state_fields(state))

    if state.get("last_action") != "blocked_tool:risky_tool":
        print_turn("warning", "Expected risky_tool to be blocked.")


def run_complete_topic_step(
    agent: Any, config: RunnableConfig, max_input_length: int
) -> None:
    """Step 4: authorised completion is recorded."""
    user_message = "Complete the production-ready agents lab and move to middleware_concept."

    validation_error = validate_input(user_message, max_input_length)

    if validation_error is not None:
        state = agent.get_state(config).values
        blocked_count = state.get("blocked_request_count", 0)
        agent.update_state(
            config,
            {
                "blocked_request_count": blocked_count + 1,
                "last_action": "blocked_input_validation",
            },
        )
        result = validation_error
    else:
        invoke_agent(agent, user_message, config)
        state = agent.get_state(config).values
        result = latest_message_to_str(state)

    print_section("Step 4: authorised completion is recorded")
    print_turn("user", user_message)
    print_turn("result", result)

    state = agent.get_state(config).values
    print_turn("state", format_state_fields(state))

    if "production_ready_agents" not in state.get("completed_topics", []):
        print_turn("warning", "Expected topic completion did not occur.")


def run_production_summary(agent: Any, config: RunnableConfig) -> None:
    """Step 5: deterministic production summary."""
    state = agent.get_state(config).values

    tool_call_count = state.get("tool_call_count", 0)
    blocked_request_count = state.get("blocked_request_count", 0)
    error_count = state.get("error_count", 0)
    last_action = state.get("last_action", "Unknown")

    summary = (
        "A production-ready agent should not rely on model behaviour alone.\n"
        "This lab used deterministic controls around the agent:\n"
        "1. Input validation (before agent invocation, not prompt-only).\n"
        "2. Tool authorisation (inside tools via is_tool_authorised).\n"
        "3. Safe blocking of unauthorised tools.\n"
        "4. Controlled state updates via Command(update={...}).\n"
        "5. Basic observability through counters and last_action.\n"
        f"Tool calls: {tool_call_count}\n"
        f"Blocked requests: {blocked_request_count}\n"
        f"Errors: {error_count}\n"
        f"Last action: {last_action}"
    )

    print_section("Production readiness summary")
    print_turn("summary", summary)
    print_turn("final state", format_state_fields(state))


def main() -> None:
    """Main entry point for Lab 12."""
    print_section("12 Production-Ready Agents")

    model = get_chat_model()

    agent = create_agent(
        model=model,
        tools=[add_learning_note, complete_topic, risky_tool],
        state_schema=ProductionState,
        checkpointer=MemorySaver(),
    )

    config: RunnableConfig = {
        "configurable": {
            "thread_id": "production-ready-agents-lab",
        }
    }

    initial_state = create_initial_state()
    agent.update_state(config, initial_state)

    state = agent.get_state(config).values
    print_turn("initial state", format_state_fields(state))

    max_input_length = 200

    run_valid_request_step(agent, config, max_input_length)
    run_invalid_input_step(agent, config, max_input_length)
    run_unauthorised_tool_step(agent, config, max_input_length)
    run_complete_topic_step(agent, config, max_input_length)
    run_production_summary(agent, config)

    print_section("Conclusion")
    print()
    print(
        "Production-ready agents need deterministic controls around the model.\n"
        "This lab combined everything learned so far:\n"
        "- AgentState for structured state\n"
        "- create_agent for framework-native agent creation\n"
        "- @tool decorator and ToolRuntime for tool registration\n"
        "- Command(update={...}) for atomic state updates\n"
        "- ToolMessage for tool result communication\n"
        "- MemorySaver + thread_id for persistence\n"
        "- RunnableConfig for invocation configuration\n"
        "\nProduction controls added:\n"
        "- Input validation BEFORE agent invocation (deterministic, not prompt-only)\n"
        "- Tool authorisation inside tools (runtime check)\n"
        "- blocked_request_count, error_count, tool_call_count for observability\n"
        "- Deterministic summary showing all production metrics\n"
        "\nMiddleware (Lab 13+) will add cross-cutting concerns."
    )


if __name__ == "__main__":
    main()