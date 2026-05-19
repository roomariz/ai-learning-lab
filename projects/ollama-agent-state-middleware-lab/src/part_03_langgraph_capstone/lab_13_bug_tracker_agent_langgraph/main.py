"""
Bug Tracker Agent with LangGraph - Interactive Custom State Demo

This lab demonstrates how to use custom state in LangGraph agents to build
a bug tracking system that persists data across conversation turns.

Example: Interactive Bug Tracker Agent
This lab builds a bug tracker that maintains:
- A list of bugs with their severity and resolution status
- Auto-incrementing bug IDs
- Tracking of last action performed
- Learner progress through topics

Step 1: Introduction to Custom State
Why Do We Need Custom State?
By default, agents only track conversation messages. But what if you need to track:
- A list of tasks with their completion status?
- Items in a shopping cart?
- Research findings across multiple searches?
- A list of bugs with their status?

This is where custom state comes in. Custom state allows your agent to maintain
structured data that persists throughout the conversation.

Step 2: Tools that Read State
Tools can access the agent's state using ToolRuntime to make decisions based
on current data (e.g., checking if budget allows a purchase, listing all bugs).

Step 3: Tools that Write State
Tools can update the agent's state using Command(update={...}) to persist
changes (e.g., adding items to cart, creating bugs, marking bugs resolved).

Step 4: State Persistence
State persists across conversation turns through the checkpointer. Using the
same thread_id, the agent remembers all changes made to state.
"""

import warnings
from typing import Any, Literal

from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.common.model import get_chat_model
from src.common.printer import print_section

# Ignore warnings to clearly see the output from cells
# This helps mitigate rapidly changing LangChain/LangGraph APIs
warnings.filterwarnings("ignore")

# Severity type for bug classification
Severity = Literal["low", "medium", "high"]


# Step 1: Define custom state by extending AgentState
# Key Points:
# - Custom state must extend AgentState
# - Define your state fields with type annotations
# - The agent now has access to these fields in addition to messages
# - AgentState fields persist across invocations, unlike message history
#   which must be resent each time
class BugState(AgentState):
    learner_name: str  # Name of the learner using the agent
    current_topic: str  # Current topic being worked on
    completed_topics: list[str]  # List of topics already completed
    last_action: str  # Track the last action performed
    notes: list[str]  # Notes taken during the session
    bugs: list[dict]  # List of bugs: [{"id": 1, "title": "...", "severity": "high", "resolved": False}, ...]
    next_bug_id: int  # Auto-incrementing ID for new bugs


# Helper function to create the initial state with default values
def initial_state() -> dict[str, Any]:
    return {
        "messages": [],
        "learner_name": "Muhammad",
        "current_topic": "bug_tracker_agent_langgraph",
        "completed_topics": ["production_ready_agents"],
        "last_action": "started_bug_tracker_lab",
        "notes": [],
        "bugs": [],
        "next_bug_id": 1,
    }


# Step 2: Tools that Read State
# Key Points:
# - Add runtime: ToolRuntime parameter to your tool function
# - Access state via runtime.state.get("field_name", default_value)
# - The runtime parameter is hidden from the LLM - it doesn't see it in the function signature
# - Tools can now make decisions based on the current state


@tool
def list_bugs(runtime: ToolRuntime) -> str:
    """List all bugs with severity and status."""
    # Read state via runtime.state - this tool reads the bugs list from state
    bugs = runtime.state.get("bugs", [])

    if not bugs:
        return "No bugs reported."

    lines = []
    for bug in bugs:
        status = "RESOLVED" if bug["resolved"] else "OPEN"
        severity = bug["severity"].upper().ljust(6)
        lines.append(
            f"[BUG-{bug['id']}] [{severity}] {status:8} | {bug['title']}"
        )

    return "\n".join(lines)


@tool
def list_bugs_by_severity(runtime: ToolRuntime) -> str:
    """List bugs sorted by severity: high, medium, then low."""
    bugs = runtime.state.get("bugs", [])

    if not bugs:
        return "No bugs reported."

    severity_rank = {"high": 0, "medium": 1, "low": 2}

    sorted_bugs = sorted(
        bugs,
        key=lambda bug: (severity_rank.get(bug["severity"], 99), bug["id"]),
    )

    lines = []
    for bug in sorted_bugs:
        status = "RESOLVED" if bug["resolved"] else "OPEN"
        severity = bug["severity"].upper().ljust(6)
        lines.append(
            f"[BUG-{bug['id']}] [{severity}] {status:8} | {bug['title']}"
        )

    return "\n".join(lines)


# Step 3: Tools that Write State
# Key Points:
# - Import Command from langgraph.types
# - Return Command(update={...}) with the fields you want to update
# - Always include a messages update with a ToolMessage for the LLM to process
# - Use runtime.tool_call_id for the tool message ID
# - Command(update={...}) is the idiomatic way to mutate state in LangGraph;
#   tools return this instead of directly editing state


@tool
def create_bug(title: str, severity: Severity, runtime: ToolRuntime) -> Command:
    """Create a new bug with a title and severity."""
    # Read current bugs from state
    bugs = runtime.state.get("bugs", [])
    # Read the next bug ID from state
    bug_id = runtime.state.get("next_bug_id", 1)

    new_bug = {
        "id": bug_id,
        "title": title,
        "severity": severity,
        "resolved": False,
    }

    updated_bugs = bugs + [new_bug]
    message = f"Created BUG-{bug_id}: {title} [{severity}]"

    # Return Command to update state - this is how tools write back to state
    return Command(
        update={
            "bugs": updated_bugs,  # Update the bugs list
            "next_bug_id": bug_id + 1,  # Increment the bug ID for next time
            "last_action": f"tool_created_bug:{bug_id}",  # Track what we did
            "messages": [
                # ToolMessage is required so the LLM knows the tool ran successfully
                ToolMessage(
                    content=message,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def resolve_bug(bug_id: int, runtime: ToolRuntime) -> Command:
    """Mark a bug as resolved."""
    bugs = runtime.state.get("bugs", [])
    updated_bugs = []

    found = False
    already_resolved = False
    bug_title = ""

    for bug in bugs:
        copied = dict(bug)

        if copied["id"] == bug_id:
            found = True
            bug_title = copied["title"]

            if copied["resolved"]:
                already_resolved = True
            else:
                copied["resolved"] = True

        updated_bugs.append(copied)

    if not found:
        message = f"BUG-{bug_id} not found."
        last_action = f"tool_resolve_notfound:{bug_id}"
        state_update = {"last_action": last_action}
    elif already_resolved:
        message = f"BUG-{bug_id} is already resolved."
        last_action = f"tool_resolve_already:{bug_id}"
        state_update = {"last_action": last_action}
    else:
        message = f"Resolved BUG-{bug_id}: {bug_title}"
        last_action = f"tool_resolved_bug:{bug_id}"
        state_update = {
            "bugs": updated_bugs,
            "last_action": last_action,
        }

    return Command(
        update={
            **state_update,
            "messages": [
                ToolMessage(
                    content=message,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def reopen_bug(bug_id: int, runtime: ToolRuntime) -> Command:
    """Reopen a resolved bug."""
    bugs = runtime.state.get("bugs", [])
    updated_bugs = []

    found = False
    already_open = False
    bug_title = ""

    for bug in bugs:
        copied = dict(bug)

        if copied["id"] == bug_id:
            found = True
            bug_title = copied["title"]

            if not copied["resolved"]:
                already_open = True
            else:
                copied["resolved"] = False

        updated_bugs.append(copied)

    if not found:
        message = f"BUG-{bug_id} not found."
        last_action = f"tool_reopen_notfound:{bug_id}"
        state_update = {"last_action": last_action}
    elif already_open:
        message = f"BUG-{bug_id} is already open."
        last_action = f"tool_reopen_already:{bug_id}"
        state_update = {"last_action": last_action}
    else:
        message = f"Reopened BUG-{bug_id}: {bug_title}"
        last_action = f"tool_reopened_bug:{bug_id}"
        state_update = {
            "bugs": updated_bugs,
            "last_action": last_action,
        }

    return Command(
        update={
            **state_update,
            "messages": [
                ToolMessage(
                    content=message,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# Step 4: State Persistence
# Key Points:
# - Pass state_schema=BugState to create_agent to use custom state
# - Use checkpointer=MemorySaver() to persist state across conversation turns
# - State is persisted with the thread_id from the config
# - The agent remembers all bugs, actions, and changes made to state
# - MemorySaver is the in-memory variant; production uses SqliteSaver or PostgresSaver

SYSTEM_PROMPT = """
                    You are a Bug Tracker Agent.

                    MANDATORY RULES:
                    - Always choose the correct built-in tool.
                    - Announce which tool you are using.
                    - NEVER paraphrase tool output.
                    - ALWAYS return exact tool output verbatim.
                    - If no tool is needed, answer normally.
                    - If request is ambiguous, ask user to choose:
                    create_bug
                    list_bugs
                    list_bugs_by_severity
                    resolve_bug
                    reopen_bug
                """


def build_agent() -> Any:
    model = get_chat_model()

    # create_agent combines model, tools, state schema, and persistence.
    # - model: The LLM that drives agent decisions
    # - tools: Functions the agent can call to read/write state
    # - state_schema: Typed fields that persist across invocations
    # - checkpointer: Storage backend for state (MemorySaver for dev, DB for prod)
    # - system_prompt: Agent behaviour instructions
    return create_agent(
        model=model,
        tools=[
            list_bugs,
            list_bugs_by_severity,
            create_bug,
            resolve_bug,
            reopen_bug,
        ],
        state_schema=BugState,  # Our custom state schema
        checkpointer=MemorySaver(),  # Persists state with thread_id
        system_prompt=SYSTEM_PROMPT,  # System prompt for agent behaviour
    )


def chat(agent: Any, message: str, config: RunnableConfig) -> Any:
    """Helper function to chat with the agent."""
    # Only inspect messages created during this turn, so old ToolMessages are not repeated.
    state_before = agent.get_state(config)
    msg_count_before = len(state_before.values.get("messages", []))

    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    messages = result["messages"]

    new_messages = messages[msg_count_before:]

    print("\nAgent:")

    has_tool_output = False
    for msg in new_messages:
        if isinstance(msg, ToolMessage):
            print(msg.content)
            has_tool_output = True

    # Fallback if no tool was used.
    if not has_tool_output:
        print(messages[-1].content)

    print()
    return result


def main() -> None:
    print_section("13 LangGraph Bug Tracker Capstone")

    print("Full framework version using:")
    print("- create_agent")
    print("- AgentState")
    print("- ToolRuntime")
    print("- Command(update={...})")
    print("- ToolMessage")
    print("- MemorySaver")
    print("- get_chat_model()")
    print()

    # Build the agent with custom state schema
    agent = build_agent()

    # Create config with thread_id for state persistence
    config: RunnableConfig = {
        "configurable": {
            "thread_id": "bug-tracker-demo",
        }
    }

    # Start with a clean initial state.
    # No scripted demo commands are run, so the learner controls the full session.
    agent.update_state(config, initial_state())

    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Bug Tracker")
    print("""
            Available commands:
            1. Create bug
            2. List all bugs
            3. List bugs by severity
            4. Resolve bug
            5. Reopen bug

            Type your command, for example:
            - Create a high severity bug titled 'Login button does not respond'
            - List bugs by severity
            - Resolve BUG-1
            """
        )
    print("Type 'quit' to exit.")
    print("=" * 60)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            final_state = agent.get_state(config).values
            print("Goodbye!")
            print(f"Final bugs: {final_state.get('bugs', [])}")
            break
        if user_input.strip():
            chat(agent, user_input, config)


if __name__ == "__main__":
    main()