import json
import re
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class ValidationState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    validation_count: int
    blocked_count: int
    validation_log: list[str]


class ValidationContext(TypedDict):
    user_id: str
    role: str
    environment: str
    max_input_length: int
    min_input_length: int
    allowed_patterns: list[str]
    blocked_patterns: list[str]


class Request(TypedDict):
    user_message: str
    tool_name: str
    payload: str


@dataclass
class ValidationRuntime:
    state: ValidationState
    context: ValidationContext

    def log_validation(self, message: str) -> None:
        self.state["validation_log"].append(message)

    def record_validation(self, action: str) -> None:
        self.state["validation_count"] += 1
        self.state["last_action"] = action

    def record_blocked(self, action: str) -> None:
        self.state["blocked_count"] += 1
        self.state["last_action"] = action


class ValidationMiddleware:
    def __init__(
        self,
        name: str,
        runtime: ValidationRuntime,
    ) -> None:
        self.name = name
        self.runtime = runtime

    def validate_length(self, message: str) -> str | None:
        ctx = self.runtime.context
        if len(message) < ctx["min_input_length"]:
            reason = f"too short (min {ctx['min_input_length']})"
            self.runtime.record_blocked(f"blocked_length:{reason}")
            self.runtime.log_validation(f"{self.name}: blocked - {reason}")
            return f"Blocked: message {reason}"

        if len(message) > ctx["max_input_length"]:
            reason = f"too long (max {ctx['max_input_length']})"
            self.runtime.record_blocked(f"blocked_length:{reason}")
            self.runtime.log_validation(f"{self.name}: blocked - {reason}")
            return f"Blocked: message {reason}"

        self.runtime.log_validation(f"{self.name}: length OK")
        return None

    def validate_patterns(self, message: str) -> str | None:
        for pattern in self.runtime.context["blocked_patterns"]:
            if re.search(pattern, message, re.IGNORECASE):
                self.runtime.record_blocked(f"blocked_pattern:{pattern}")
                self.runtime.log_validation(
                    f"{self.name}: blocked - matched pattern '{pattern}'"
                )
                return f"Blocked: message contains a restricted pattern."

        for pattern in self.runtime.context["allowed_patterns"]:
            if re.search(pattern, message):
                self.runtime.log_validation(f"{self.name}: pattern '{pattern}' matched")
                return None

        self.runtime.log_validation(f"{self.name}: no allowed pattern matched")
        return None

    def validate_not_empty(self, message: str) -> str | None:
        if not message.strip():
            self.runtime.record_blocked("blocked_empty")
            self.runtime.log_validation(f"{self.name}: blocked - empty")
            return "Blocked: message is empty."

        self.runtime.log_validation(f"{self.name}: not empty")
        return None

    def validate_sanitised(self, message: str) -> str | None:
        sanitised = message.strip()
        if sanitised != message:
            self.runtime.log_validation(
                f"{self.name}: sanitised (stripped whitespace)"
            )

        control_chars = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
        if control_chars.search(message):
            self.runtime.record_blocked("blocked_control_chars")
            self.runtime.log_validation(f"{self.name}: blocked - control characters")
            return "Blocked: message contains control characters."

        self.runtime.log_validation(f"{self.name}: sanitised OK")
        return None


def create_state() -> ValidationState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "input_validation_middleware",
        "completed_topics": [
            "production_ready_agents",
            "middleware_concept",
            "middleware_hooks",
        ],
        "last_action": "started_input_validation_lab",
        "notes": [],
        "validation_count": 0,
        "blocked_count": 0,
        "validation_log": [],
    }


def create_context() -> ValidationContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "min_input_length": 3,
        "max_input_length": 120,
        "allowed_patterns": [r"\w+"],
        "blocked_patterns": [r"<script", r"javascript:", r"on\w+="],
    }


def format_json(data: ValidationState | ValidationContext) -> str:
    return json.dumps(data, indent=2)


def run_empty_input_test(runtime: ValidationRuntime) -> None:
    middleware = ValidationMiddleware("input_validator", runtime)

    result = middleware.validate_not_empty("")
    result = result or middleware.validate_length("")
    result = result or middleware.validate_patterns("")

    print_section("Step 1: empty input is blocked")
    print_turn("input", repr(""))
    print_turn("result", result or "passed")


def run_too_short_test(runtime: ValidationRuntime) -> None:
    middleware = ValidationMiddleware("input_validator", runtime)

    result = middleware.validate_not_empty("ab")
    result = result or middleware.validate_length("ab")
    result = result or middleware.validate_patterns("ab")

    print_section("Step 2: too-short input is blocked")
    print_turn("input", repr("ab"))
    print_turn("result", result or "passed")


def run_too_long_test(runtime: ValidationRuntime) -> None:
    middleware = ValidationMiddleware("input_validator", runtime)

    long_message = "A" * 200

    result = middleware.validate_not_empty(long_message)
    result = result or middleware.validate_length(long_message)
    result = result or middleware.validate_patterns(long_message)

    print_section("Step 3: too-long input is blocked")
    print_turn("input", repr(long_message[:40] + "..."))
    print_turn("length", str(len(long_message)))
    print_turn("result", result or "passed")


def run_xss_pattern_test(runtime: ValidationRuntime) -> None:
    middleware = ValidationMiddleware("input_validator", runtime)

    result = middleware.validate_not_empty("<script>alert('xss')</script>")
    result = result or middleware.validate_length("<script>alert('xss')</script>")
    result = result or middleware.validate_patterns("<script>alert('xss')</script>")

    print_section("Step 4: XSS pattern is blocked")
    print_turn("input", repr("<script>alert('xss')</script>"))
    print_turn("result", result or "passed")


def run_valid_input_test(runtime: ValidationRuntime) -> None:
    middleware = ValidationMiddleware("input_validator", runtime)

    message = "Add a note about input validation."

    result = middleware.validate_not_empty(message)
    result = result or middleware.validate_length(message)
    result = result or middleware.validate_patterns(message)

    print_section("Step 5: valid input passes")
    print_turn("input", repr(message))
    print_turn("result", result or "passed")


def run_validation_summary(runtime: ValidationRuntime) -> None:
    summary = (
        "Input validation middleware runs before the tool.\n"
        "It checks length, patterns, emptiness, and sanitisation.\n"
        f"Total validations: {runtime.state['validation_count']}\n"
        f"Blocked inputs: {runtime.state['blocked_count']}"
    )

    print_section("Input validation summary")
    print_turn("summary", summary)
    print_turn("validation log", format_json(runtime.state["validation_log"]))
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("16 Input Validation Middleware")

    state = create_state()
    context = create_context()
    runtime = ValidationRuntime(state=state, context=context)

    print_turn("initial context", format_json(context))

    run_empty_input_test(runtime)
    run_too_short_test(runtime)
    run_too_long_test(runtime)
    run_xss_pattern_test(runtime)
    run_valid_input_test(runtime)
    run_validation_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Input validation middleware protects the system from bad or malicious input. "
        "Length limits, pattern blocks, and sanitisation checks prevent common attacks and errors before they reach the tool layer."
    )


if __name__ == "__main__":
    main()