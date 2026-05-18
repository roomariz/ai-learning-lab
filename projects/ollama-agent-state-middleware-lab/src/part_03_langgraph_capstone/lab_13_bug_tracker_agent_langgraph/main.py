import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class BugState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    bugs: list[dict]
    next_bug_id: int


class BugContext(TypedDict):
    user_id: str
    role: str
    environment: str
    authorised_tools: list[str]


@dataclass
class BugRuntime:
    state: BugState
    context: BugContext

    def record_action(self, action: str) -> None:
        self.state["last_action"] = action

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]


def create_state() -> BugState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "bug_tracker_agent_langgraph",
        "completed_topics": [
            "production_ready_agents",
        ],
        "last_action": "started_bug_tracker_lab",
        "notes": [],
        "bugs": [],
        "next_bug_id": 1,
    }


def create_context() -> BugContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "authorised_tools": [
            "list_bugs",
            "create_bug",
            "resolve_bug",
            "reopen_bug",
        ],
    }


def format_json(data: BugState | BugContext) -> str:
    return json.dumps(data, indent=2)


def list_bugs_tool(runtime: BugRuntime) -> str:
    tool_name = "list_bugs"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    bugs = runtime.state["bugs"]

    if not bugs:
        return "No bugs reported."

    lines = []
    for bug in bugs:
        status = "RESOLVED" if bug["resolved"] else "OPEN"
        lines.append(
            f"[BUG-{bug['id']}] [{bug['severity'].upper():5}] {status:8} | {bug['title']}"
        )

    runtime.record_action("tool_list_bugs")
    return "\n".join(lines)


def create_bug_tool(
    runtime: BugRuntime,
    title: str,
    severity: str,
) -> str:
    tool_name = "create_bug"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    bug_id = runtime.state["next_bug_id"]

    bug = {
        "id": bug_id,
        "title": title,
        "severity": severity,
        "resolved": False,
    }

    runtime.state["bugs"].append(bug)
    runtime.state["next_bug_id"] += 1
    runtime.record_action(f"tool_created_bug:{bug_id}")

    return f"Created BUG-{bug_id}: {title} [{severity}]"


def resolve_bug_tool(runtime: BugRuntime, bug_id: int) -> str:
    tool_name = "resolve_bug"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    bugs = runtime.state["bugs"]
    target = next((b for b in bugs if b["id"] == bug_id), None)

    if target is None:
        runtime.record_action(f"tool_resolve_not_found:{bug_id}")
        return f"Bug not found: BUG-{bug_id}"

    if target["resolved"]:
        runtime.record_action(f"tool_resolve_already:{bug_id}")
        return f"BUG-{bug_id} is already resolved."

    target["resolved"] = True
    runtime.record_action(f"tool_resolved_bug:{bug_id}")

    return f"Resolved BUG-{bug_id}: {target['title']}"


def reopen_bug_tool(runtime: BugRuntime, bug_id: int) -> str:
    tool_name = "reopen_bug"

    if not runtime.is_tool_authorised(tool_name):
        return f"Tool blocked: {tool_name}"

    bugs = runtime.state["bugs"]
    target = next((b for b in bugs if b["id"] == bug_id), None)

    if target is None:
        runtime.record_action(f"tool_reopen_not_found:{bug_id}")
        return f"Bug not found: BUG-{bug_id}"

    if not target["resolved"]:
        runtime.record_action(f"tool_reopen_already:{bug_id}")
        return f"BUG-{bug_id} is already open."

    target["resolved"] = False
    runtime.record_action(f"tool_reopened_bug:{bug_id}")

    return f"Reopened BUG-{bug_id}: {target['title']}"


def run_list_bugs_step(runtime: BugRuntime) -> None:
    user_message = "Show all current bugs."
    result = list_bugs_tool(runtime)

    print_section("Step 1: list all bugs (empty)")
    print_turn("user", user_message)
    print_turn("tool result", result)


def run_create_bugs_step(runtime: BugRuntime) -> None:
    user_message = "Report three bugs in the codebase."

    result1 = create_bug_tool(runtime, "Login button does not respond", "high")
    result2 = create_bug_tool(runtime, "Dark mode icon misaligned", "low")
    result3 = create_bug_tool(runtime, "API timeout on large payloads", "medium")

    print_section("Step 2: create three bugs")
    print_turn("user", user_message)
    print_turn("BUG-1", result1)
    print_turn("BUG-2", result2)
    print_turn("BUG-3", result3)
    print_turn("bug state", format_json(runtime.state))


def run_list_after_create_step(runtime: BugRuntime) -> None:
    user_message = "List bugs after creation."
    result = list_bugs_tool(runtime)

    print_section("Step 3: list bugs after creation")
    print_turn("user", user_message)
    print_turn("tool result", result)


def run_resolve_bugs_step(runtime: BugRuntime) -> None:
    user_message = "Mark the high-severity bug as resolved."

    result = resolve_bug_tool(runtime, bug_id=1)

    print_section("Step 4: resolve high-severity bug")
    print_turn("user", user_message)
    print_turn("tool result", result)
    print_turn("bug state", format_json(runtime.state))


def run_resolve_invalid_step(runtime: BugRuntime) -> None:
    user_message = "Try to resolve an already resolved bug."

    result = resolve_bug_tool(runtime, bug_id=1)

    print_section("Step 5: resolve already-resolved bug")
    print_turn("user", user_message)
    print_turn("tool result", result)


def run_reopen_bug_step(runtime: BugRuntime) -> None:
    user_message = "Reopen the dark mode bug."

    result = reopen_bug_tool(runtime, bug_id=2)

    print_section("Step 6: attempt to reopen an already-open bug")
    print_turn("user", user_message)
    print_turn("tool result", result)
    print_turn("bug state", format_json(runtime.state))


def run_bug_summary(runtime: BugRuntime) -> None:
    open_count = sum(1 for b in runtime.state["bugs"] if not b["resolved"])
    resolved_count = sum(1 for b in runtime.state["bugs"] if b["resolved"])

    summary = (
        "Bug tracking keeps a structured record of issues and their resolution.\n"
        f"Total bugs: {len(runtime.state['bugs'])}\n"
        f"Open: {open_count}\n"
        f"Resolved: {resolved_count}\n"
        f"Next bug ID: {runtime.state['next_bug_id']}"
    )

    print_section("Bug tracker summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("13 Bug Tracker Agent with LangGraph")

    state = create_state()
    context = create_context()
    runtime = BugRuntime(state=state, context=context)

    print_turn("initial context", format_json(runtime.context))
    print_turn("initial state", format_json(runtime.state))

    run_list_bugs_step(runtime)
    run_create_bugs_step(runtime)
    run_list_after_create_step(runtime)
    run_resolve_bugs_step(runtime)
    run_resolve_invalid_step(runtime)
    run_reopen_bug_step(runtime)
    run_bug_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "A bug tracker agent keeps bugs in state so they persist across turns. "
        "State mutation through tools like create, resolve, and reopen mirrors real engineering workflows."
    )


if __name__ == "__main__":
    main()