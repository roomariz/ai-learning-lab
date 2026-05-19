import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class ErrorState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    error_count: int
    errors_recovered: int
    error_log: list[str]


class ErrorContext(TypedDict):
    user_id: str
    role: str
    environment: str
    retry_on_errors: bool
    max_retries: int


class Request(TypedDict):
    user_message: str
    tool_name: str
    payload: str


@dataclass
class ErrorRuntime:
    state: ErrorState
    context: ErrorContext

    def log_error(self, entry: dict) -> None:
        self.state["error_log"].append(entry)

    def record_error(self) -> None:
        self.state["error_count"] += 1

    def record_recovery(self) -> None:
        self.state["errors_recovered"] += 1

    def record_action(self, action: str) -> None:
        self.state["last_action"] = action


# Error handling middleware prevents tool failures from breaking the agent loop.
# Production agents need fallback values, retry logic, and error logging.
class ErrorHandlingMiddleware:
    def __init__(self, runtime: ErrorRuntime) -> None:
        self.runtime = runtime

    def handle_tool_error(
        self,
        tool_name: str,
        error: Exception,
    ) -> str:
        error_type = type(error).__name__
        self.runtime.record_error()
        self.runtime.record_action(f"error:{error_type}:{tool_name}")

        self.runtime.log_error({
            "tool": tool_name,
            "error_type": error_type,
            "message": str(error),
            "recovered": False,
        })

        return f"Error in {tool_name} ({error_type}): {error}"

    def handle_with_fallback(
        self,
        tool_name: str,
        error: Exception,
        fallback_value: str,
    ) -> str:
        error_type = type(error).__name__
        self.runtime.record_error()
        self.runtime.record_recovery()

        self.runtime.log_error({
            "tool": tool_name,
            "error_type": error_type,
            "message": str(error),
            "recovered": True,
            "fallback_used": True,
        })

        return fallback_value

    def handle_with_retry(
        self,
        tool_name: str,
        error: Exception,
    ) -> str:
        error_type = type(error).__name__
        self.runtime.record_error()

        self.runtime.log_error({
            "tool": tool_name,
            "error_type": error_type,
            "message": str(error),
            "recovered": False,
            "retry_attempted": self.runtime.context["retry_on_errors"],
        })

        return f"Error in {tool_name} ({error_type}): {error}. Retry: {self.runtime.context['retry_on_errors']}"


def create_state() -> ErrorState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "error_handling_middleware",
        "completed_topics": [
            "production_ready_agents",
            "middleware_concept",
            "middleware_hooks",
            "input_validation_middleware",
            "tool_authorisation",
        ],
        "last_action": "started_error_handling_lab",
        "notes": [],
        "error_count": 0,
        "errors_recovered": 0,
        "error_log": [],
    }


def create_context() -> ErrorContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "retry_on_errors": True,
        "max_retries": 3,
    }


def format_json(data: ErrorState | ErrorContext) -> str:
    return json.dumps(data, indent=2)


def risky_tool(runtime: ErrorRuntime) -> str:
    raise RuntimeError("Simulated tool failure.")


def failing_lookup_tool(runtime: ErrorRuntime, key: str) -> str:
    raise KeyError(f"Key not found: {key}")


def run_basic_error_handling(runtime: ErrorRuntime) -> None:
    middleware = ErrorHandlingMiddleware(runtime)

    try:
        result = risky_tool(runtime)
    except Exception as e:
        result = middleware.handle_tool_error("risky_tool", e)

    print_section("Step 1: tool error is caught and reported")
    print_turn("tool", "risky_tool")
    print_turn("result", result)
    print_turn("error_count", str(runtime.state["error_count"]))


def run_key_error_handling(runtime: ErrorRuntime) -> None:
    middleware = ErrorHandlingMiddleware(runtime)

    try:
        result = failing_lookup_tool(runtime, "missing_key")
    except Exception as e:
        result = middleware.handle_tool_error("failing_lookup_tool", e)

    print_section("Step 2: KeyError is caught and reported")
    print_turn("tool", "failing_lookup_tool")
    print_turn("result", result)
    print_turn("error_count", str(runtime.state["error_count"]))


def run_fallback_recovery(runtime: ErrorRuntime) -> None:
    middleware = ErrorHandlingMiddleware(runtime)

    try:
        result = failing_lookup_tool(runtime, "fallback_key")
    except Exception as e:
        result = middleware.handle_with_fallback(
            "failing_lookup_tool",
            e,
            fallback_value="Fallback: key not found, returning empty list.",
        )

    print_section("Step 3: error handled with fallback")
    print_turn("tool", "failing_lookup_tool")
    print_turn("result", result)
    print_turn("errors_recovered", str(runtime.state["errors_recovered"]))


def run_retry_info(runtime: ErrorRuntime) -> None:
    middleware = ErrorHandlingMiddleware(runtime)

    try:
        result = risky_tool(runtime)
    except Exception as e:
        result = middleware.handle_with_retry("risky_tool", e)

    print_section("Step 4: error with retry info")
    print_turn("tool", "risky_tool")
    print_turn("retry_enabled", str(runtime.context["retry_on_errors"]))
    print_turn("max_retries", str(runtime.context["max_retries"]))
    print_turn("result", result)


def run_error_summary(runtime: ErrorRuntime) -> None:
    summary = (
        "Error handling middleware catches exceptions from tools.\n"
        "It can report errors, fall back to safe defaults, or flag for retry.\n"
        f"Total errors: {runtime.state['error_count']}\n"
        f"Recovered with fallback: {runtime.state['errors_recovered']}\n"
        f"Error log entries: {len(runtime.state['error_log'])}"
    )

    print_section("Error handling summary")
    print_turn("summary", summary)
    print_turn("error log", format_json(runtime.state["error_log"]))
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("18 Error Handling Middleware")

    state = create_state()
    context = create_context()
    runtime = ErrorRuntime(state=state, context=context)

    print_turn("initial context", format_json(context))

    run_basic_error_handling(runtime)
    run_key_error_handling(runtime)
    run_fallback_recovery(runtime)
    run_retry_info(runtime)
    run_error_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Error handling middleware catches exceptions from tools. "
        "It can report errors safely, fall back to default values, or flag the error for retry. "
        "Without it, unhandled tool errors propagate up and break the agent loop."
    )


if __name__ == "__main__":
    main()