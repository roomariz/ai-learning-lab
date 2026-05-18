from dataclasses import dataclass
from typing import Callable, TypedDict

from src.common.printer import print_section, print_turn


class HookState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    hook_log: list[str]
    tool_call_count: int
    blocked_request_count: int


class HookContext(TypedDict):
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
class HookRuntime:
    state: HookState
    context: HookContext

    def log_hook(self, hook_name: str, phase: str) -> None:
        self.state["hook_log"].append(f"{phase}:{hook_name}")

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action

    def record_blocked_request(self, action: str) -> None:
        self.state["blocked_request_count"] += 1
        self.state["last_action"] = action

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]


MiddlewareResult = str | None
MiddlewareHook = (
    None
    | Callable[[HookRuntime, Request], MiddlewareResult]
    | Callable[[HookRuntime], None]
)


def create_state() -> HookState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "middleware_hooks",
        "completed_topics": [
            "production_ready_agents",
            "middleware_concept",
        ],
        "last_action": "started_middleware_hooks_lab",
        "notes": [],
        "hook_log": [],
        "tool_call_count": 0,
        "blocked_request_count": 0,
    }


def create_context() -> HookContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "authorised_tools": [
            "add_note",
            "complete_topic",
        ],
        "max_input_length": 120,
    }


def format_json(data: HookState | HookContext | Request) -> str:
    return json.dumps(data, indent=2)


class MiddlewareWithHooks:
    def __init__(self, name: str) -> None:
        self.name = name
        self.before_request_calls = 0
        self.after_request_calls = 0
        self.on_error_calls = 0

    def before_request(
        self,
        runtime: HookRuntime,
        request: Request,
    ) -> MiddlewareResult:
        self.before_request_calls += 1
        runtime.log_hook(self.name, "before_request")
        return None

    def after_request(
        self,
        runtime: HookRuntime,
        request: Request,
        result: str,
    ) -> None:
        self.after_request_calls += 1
        runtime.log_hook(self.name, "after_request")

    def on_error(
        self,
        runtime: HookRuntime,
        request: Request,
        error: Exception,
    ) -> None:
        self.on_error_calls += 1
        runtime.log_hook(self.name, f"on_error:{type(error).__name__}")


input_validation = MiddlewareWithHooks("input_validation")
tool_auth = MiddlewareWithHooks("tool_auth")
audit = MiddlewareWithHooks("audit")


def input_validation_check(
    runtime: HookRuntime,
    request: Request,
) -> MiddlewareResult:
    runtime.log_hook("input_validation", "check")
    user_message = request["user_message"]

    if not user_message.strip():
        runtime.record_blocked_request("blocked_empty_input")
        return "Blocked: message is empty."

    if len(user_message) > runtime.context["max_input_length"]:
        runtime.record_blocked_request("blocked_input_too_long")
        return "Blocked: message is too long."

    return None


def tool_auth_check(
    runtime: HookRuntime,
    request: Request,
) -> MiddlewareResult:
    runtime.log_hook("tool_auth", "check")
    tool_name = request["tool_name"]

    if not runtime.is_tool_authorised(tool_name):
        runtime.record_blocked_request(f"blocked_tool:{tool_name}")
        return f"Blocked: {tool_name}"

    return None


def audit_log(
    runtime: HookRuntime,
    request: Request,
) -> None:
    runtime.log_hook("audit", "log")
    pass


def add_note_tool(runtime: HookRuntime, payload: str) -> str:
    runtime.state["notes"].append(payload)
    runtime.record_tool_call("tool_add_note")
    return f"Note added: {payload}"


def complete_topic_tool(runtime: HookRuntime, topic: str) -> str:
    if topic not in runtime.state["completed_topics"]:
        runtime.state["completed_topics"].append(topic)

    runtime.state["current_topic"] = "middleware_hooks"
    runtime.record_tool_call("tool_complete_topic")
    return f"Completed {topic}; next topic is middleware_hooks."


def run_tool(
    runtime: HookRuntime,
    request: Request,
) -> str:
    if request["tool_name"] == "add_note":
        return add_note_tool(runtime, request["payload"])

    if request["tool_name"] == "complete_topic":
        return complete_topic_tool(runtime, request["payload"])

    runtime.record_blocked_request(f"unknown_tool:{request['tool_name']}")
    return f"Unknown tool: {request['tool_name']}"


def handle_request(
    runtime: HookRuntime,
    request: Request,
    middleware: list[MiddlewareWithHooks],
) -> str:
    for mw in middleware:
        mw.before_request(runtime, request)

    for mw in middleware:
        result = input_validation_check(runtime, request)
        if result is not None:
            for mw2 in middleware:
                mw2.after_request(runtime, request, result)
            return result

        result = tool_auth_check(runtime, request)
        if result is not None:
            for mw2 in middleware:
                mw2.after_request(runtime, request, result)
            return result

    result = run_tool(runtime, request)

    for mw in reversed(middleware):
        mw.after_request(runtime, request, result)

    return result


def run_hooks_overview(runtime: HookRuntime) -> None:
    print_section("Middleware hook phases")
    print_turn("before_request", "Called before any checks run.")
    print_turn("check (middle)", "Validation or authorisation logic.")
    print_turn("after_request", "Called after the request is handled.")
    print_turn("on_error", "Called when an exception propagates.")
    print_turn(
        "hook_log (empty)",
        format_json(runtime.state["hook_log"]),
    )


def run_normal_request_step(
    runtime: HookRuntime,
    middleware: list[MiddlewareWithHooks],
) -> None:
    request: Request = {
        "user_message": "Add a note about middleware hooks.",
        "tool_name": "add_note",
        "payload": "Hooks separate lifecycle concerns cleanly.",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 1: normal request with all hook phases")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("hook_log", format_json(runtime.state["hook_log"]))


def run_blocked_request_step(
    runtime: HookRuntime,
    middleware: list[MiddlewareWithHooks],
) -> None:
    request: Request = {
        "user_message": "",
        "tool_name": "add_note",
        "payload": "Should not be added.",
    }

    result = handle_request(runtime, request, middleware)

    print_section("Step 2: blocked request stops after check")
    print_turn("request", format_json(request))
    print_turn("result", result)
    print_turn("hook_log", format_json(runtime.state["hook_log"]))


def run_hooks_summary(runtime: HookRuntime) -> None:
    hook_counts = {}
    for entry in runtime.state["hook_log"]:
        phase, name = entry.split(":", 1)
        key = f"{name}.{phase}"
        hook_counts[key] = hook_counts.get(key, 0) + 1

    lines = [f"{name}.{phase}: {count}" for name, phase, count in [
        (name, phase, count)
        for (name, phase), count in [
            ((k.split(".")[0], k.split(".")[1]), v)
            for k, v in hook_counts.items()
        ]
    ]]

    summary = (
        "Hooks give middleware a lifecycle: before, during, after, on_error.\n"
        f"Tool calls: {runtime.state['tool_call_count']}\n"
        f"Blocked: {runtime.state['blocked_request_count']}\n"
        f"Total hook calls: {len(runtime.state['hook_log'])}"
    )

    print_section("Hooks summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("15 Middleware Hooks")

    state = create_state()
    context = create_context()
    runtime = HookRuntime(state=state, context=context)

    print_turn("initial context", format_json(runtime.context))

    middleware: list[MiddlewareWithHooks] = [
        input_validation,
        tool_auth,
        audit,
    ]

    run_hooks_overview(runtime)
    run_normal_request_step(runtime, middleware)
    run_blocked_request_step(runtime, middleware)
    run_hooks_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Middleware hooks separate lifecycle concerns: before, during, after, and on_error. "
        "This makes it easier to add logging, metrics, or cleanup without mixing it into business logic."
    )


if __name__ == "__main__":
    main()