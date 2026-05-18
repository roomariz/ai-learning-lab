import json
from dataclasses import dataclass
from typing import Callable, TypedDict

from src.common.printer import print_section, print_turn


class MiddlewareState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    tool_call_count: int
    blocked_request_count: int
    middleware_trace: list[str]


class MiddlewareContext(TypedDict):
    user_id: str
    role: str
    environment: str
    authorised_tools: list[str]
    max_input_length: int


class Request(TypedDict):
    user_message: str
    tool_name: str
    payload: str


@dataclass
class MiddlewareRuntime:
    state: MiddlewareState
    context: MiddlewareContext

    def record_trace(self, name: str) -> None:
        self.state["middleware_trace"].append(name)

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action

    def record_blocked_request(self, action: str) -> None:
        self.state["blocked_request_count"] += 1
        self.state["last_action"] = action

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]


MiddlewareResult = str | None
Middleware = Callable[[MiddlewareRuntime, Request], MiddlewareResult]


def create_state() -> MiddlewareState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "middleware_concept",
        "completed_topics": [
            "production_ready_agents",
        ],
        "last_action": "started_middleware_concept_lab",
        "notes": [],
        "tool_call_count": 0,
        "blocked_request_count": 0,
        "middleware_trace": [],
    }


def create_context() -> MiddlewareContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "authorised_tools": [
            "add_learning_note",
            "complete_topic",
        ],
        "max_input_length": 120,
    }


def format_json(data: MiddlewareState | MiddlewareContext | Request) -> str:
    return json.dumps(data, indent=2)


def input_validation_middleware(
    runtime: MiddlewareRuntime,
    request: Request,
) -> MiddlewareResult:
    runtime.record_trace("input_validation_middleware")

    user_message = request["user_message"]

    if not user_message.strip():
        runtime.record_blocked_request("blocked_empty_input")
        return "Input blocked by middleware: message is empty."

    if len(user_message) > runtime.context["max_input_length"]:
        runtime.record_blocked_request("blocked_input_too_long")
        return "Input blocked by middleware: message is too long."

    return None


def tool_authorisation_middleware(
    runtime: MiddlewareRuntime,
    request: Request,
) -> MiddlewareResult:
    runtime.record_trace("tool_authorisation_middleware")

    tool_name = request["tool_name"]

    if not runtime.is_tool_authorised(tool_name):
        runtime.record_blocked_request(f"blocked_tool:{tool_name}")
        return f"Tool blocked by middleware: {tool_name}"

    return None


def audit_middleware(
    runtime: MiddlewareRuntime,
    request: Request,
) -> MiddlewareResult:
    runtime.record_trace("audit_middleware")
    return None


def add_learning_note_tool(
    runtime: MiddlewareRuntime,
    payload: str,
) -> str:
    runtime.state["notes"].append(payload)
    runtime.record_tool_call("tool_added_learning_note")
    return f"Note added: {payload}"


def complete_topic_tool(
    runtime: MiddlewareRuntime,
    payload: str,
) -> str:
    topic = payload

    if topic not in runtime.state["completed_topics"]:
        runtime.state["completed_topics"].append(topic)

    runtime.state["current_topic"] = "middleware_hooks"
    runtime.record_tool_call("tool_completed_topic")

    return f"Completed {topic}; next topic is middleware_hooks."


def run_tool(
    runtime: MiddlewareRuntime,
    request: Request,
) -> str:
    if request["tool_name"] == "add_learning_note":
        return add_learning_note_tool(runtime, request["payload"])

    if request["tool_name"] == "complete_topic":
        return complete_topic_tool(runtime, request["payload"])

    runtime.record_blocked_request(f"unknown_tool:{request['tool_name']}")
    return f"Unknown tool: {request['tool_name']}"


def handle_request(
    runtime: MiddlewareRuntime,
    request: Request,
    middleware: list[Middleware],
) -> str:
    for item in middleware:
        result = item(runtime, request)
        if result is not None:
            return result

    return run_tool(runtime, request)


def run_valid_request_step(runtime: MiddlewareRuntime, middleware: list[Middleware]) -> None:
    request: Request = {
        "user_message": "Add a note about middleware.",
        "tool_name": "add_learning_note",
        "payload": "Middleware separates control logic from tool logic.",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 1: valid request passes middleware")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_invalid_input_step(runtime: MiddlewareRuntime, middleware: list[Middleware]) -> None:
    request: Request = {
        "user_message": "",
        "tool_name": "add_learning_note",
        "payload": "This should not be added.",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 2: invalid input stops before tool")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_unauthorised_tool_step(
    runtime: MiddlewareRuntime,
    middleware: list[Middleware],
) -> None:
    request: Request = {
        "user_message": "Run an admin-only tool.",
        "tool_name": "delete_all_notes",
        "payload": "",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 3: unauthorised tool stops before tool")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_complete_topic_step(runtime: MiddlewareRuntime, middleware: list[Middleware]) -> None:
    request: Request = {
        "user_message": "Complete the middleware concept lab.",
        "tool_name": "complete_topic",
        "payload": "middleware_concept",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 4: completion request passes middleware")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_middleware_summary(runtime: MiddlewareRuntime) -> None:
    summary = (
        "Middleware is control logic that runs before the tool.\n"
        "In this lab, middleware handled validation, authorisation, and auditing.\n"
        "The tool functions stayed focused on their actual job.\n"
        f"Tool calls: {runtime.state['tool_call_count']}\n"
        f"Blocked requests: {runtime.state['blocked_request_count']}\n"
        f"Middleware calls recorded: {len(runtime.state['middleware_trace'])}"
    )

    print_section("Middleware summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))
    print_turn("context", format_json(runtime.context))


def main() -> None:
    print_section("13 Middleware Concept")

    state = create_state()
    context = create_context()
    runtime = MiddlewareRuntime(state=state, context=context)

    middleware: list[Middleware] = [
        input_validation_middleware,
        tool_authorisation_middleware,
        audit_middleware,
    ]

    print_turn("initial context", format_json(runtime.context))
    print_turn("initial state", format_json(runtime.state))

    run_valid_request_step(runtime, middleware)
    run_invalid_input_step(runtime, middleware)
    run_unauthorised_tool_step(runtime, middleware)
    run_complete_topic_step(runtime, middleware)
    run_middleware_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Middleware keeps production controls separate from tool logic. "
        "This makes validation, authorisation, auditing, and later error handling easier to reason about."
    )


if __name__ == "__main__":
    main()