import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class ProductionState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    tool_call_count: int
    blocked_request_count: int
    error_count: int


class ProductionContext(TypedDict):
    user_id: str
    role: str
    environment: str
    authorised_tools: list[str]
    max_input_length: int


@dataclass
class ProductionRuntime:
    state: ProductionState
    context: ProductionContext

    def record_action(self, action: str) -> None:
        self.state["last_action"] = action

    def record_tool_call(self, action: str) -> None:
        self.state["tool_call_count"] += 1
        self.state["last_action"] = action

    def record_blocked_request(self, action: str) -> None:
        self.state["blocked_request_count"] += 1
        self.state["last_action"] = action

    def record_error(self, action: str) -> None:
        self.state["error_count"] += 1
        self.state["last_action"] = action

    def is_tool_authorised(self, tool_name: str) -> bool:
        return tool_name in self.context["authorised_tools"]


def create_state() -> ProductionState:
    return {
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
    }


def create_context() -> ProductionContext:
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


def format_json(data: ProductionState | ProductionContext) -> str:
    return json.dumps(data, indent=2)


def validate_input(runtime: ProductionRuntime, user_input: str) -> str | None:
    if not user_input.strip():
        runtime.record_blocked_request("blocked_empty_input")
        return "Input blocked: message is empty."

    if len(user_input) > runtime.context["max_input_length"]:
        runtime.record_blocked_request("blocked_input_too_long")
        return "Input blocked: message is too long."

    return None


def require_tool_authorisation(
    runtime: ProductionRuntime,
    tool_name: str,
) -> str | None:
    if not runtime.is_tool_authorised(tool_name):
        runtime.record_blocked_request(f"blocked_tool:{tool_name}")
        return f"Tool blocked: {tool_name}"

    return None


def add_learning_note_tool(runtime: ProductionRuntime, note: str) -> str:
    tool_name = "add_learning_note"

    blocked_reason = require_tool_authorisation(runtime, tool_name)
    if blocked_reason is not None:
        return blocked_reason

    runtime.state["notes"].append(note)
    runtime.record_tool_call("tool_added_learning_note")

    return f"Note added: {note}"


def complete_topic_tool(
    runtime: ProductionRuntime,
    topic: str,
    next_topic: str,
) -> str:
    tool_name = "complete_topic"

    blocked_reason = require_tool_authorisation(runtime, tool_name)
    if blocked_reason is not None:
        return blocked_reason

    if topic not in runtime.state["completed_topics"]:
        runtime.state["completed_topics"].append(topic)

    runtime.state["current_topic"] = next_topic
    runtime.record_tool_call("tool_completed_topic")

    return f"Completed {topic}; next topic is {next_topic}."


def risky_tool(runtime: ProductionRuntime) -> str:
    tool_name = "risky_tool"

    blocked_reason = require_tool_authorisation(runtime, tool_name)
    if blocked_reason is not None:
        return blocked_reason

    try:
        raise RuntimeError("Simulated production tool failure.")
    except RuntimeError:
        runtime.record_error("tool_error:risky_tool")
        return "Tool failed safely: risky_tool"


def run_valid_request_step(runtime: ProductionRuntime) -> None:
    user_message = "Add a note about production-ready agents."
    note = "Production agents need validation, authorisation, error handling, and observability."

    validation_error = validate_input(runtime, user_message)

    if validation_error is not None:
        result = validation_error
    else:
        result = add_learning_note_tool(runtime, note)

    print_section("Step 1: valid request is processed")
    print_turn("user", user_message)
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_invalid_input_step(runtime: ProductionRuntime) -> None:
    user_message = ""

    validation_error = validate_input(runtime, user_message)

    print_section("Step 2: invalid input is blocked")
    print_turn("user", "<empty message>")
    print_turn("result", validation_error or "Input accepted.")
    print_turn("state", format_json(runtime.state))


def run_unauthorised_tool_step(runtime: ProductionRuntime) -> None:
    user_message = "Run the risky production tool."

    validation_error = validate_input(runtime, user_message)

    if validation_error is not None:
        result = validation_error
    else:
        result = risky_tool(runtime)

    print_section("Step 3: unauthorised tool is blocked")
    print_turn("user", user_message)
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_complete_topic_step(runtime: ProductionRuntime) -> None:
    user_message = "Complete the production-ready agents lab."

    validation_error = validate_input(runtime, user_message)

    if validation_error is not None:
        result = validation_error
    else:
        result = complete_topic_tool(
            runtime=runtime,
            topic="production_ready_agents",
            next_topic="middleware_concept",
        )

    print_section("Step 4: authorised completion is recorded")
    print_turn("user", user_message)
    print_turn("result", result)
    print_turn("state", format_json(runtime.state))


def run_production_summary(runtime: ProductionRuntime) -> None:
    summary = (
        "A production-ready agent should not rely on model behaviour alone.\n"
        "This lab used deterministic controls around the agent:\n"
        "1. Input validation.\n"
        "2. Tool authorisation.\n"
        "3. Safe blocking of unauthorised tools.\n"
        "4. Controlled state updates.\n"
        "5. Basic observability through counters and last_action.\n"
        f"Tool calls: {runtime.state['tool_call_count']}\n"
        f"Blocked requests: {runtime.state['blocked_request_count']}\n"
        f"Errors: {runtime.state['error_count']}"
    )

    print_section("Production readiness summary")
    print_turn("summary", summary)
    print_turn("final state", format_json(runtime.state))
    print_turn("context", format_json(runtime.context))


def main() -> None:
    print_section("12 Production-Ready Agents")

    state = create_state()
    context = create_context()
    runtime = ProductionRuntime(state=state, context=context)

    print_turn("initial context", format_json(runtime.context))
    print_turn("initial state", format_json(runtime.state))

    run_valid_request_step(runtime)
    run_invalid_input_step(runtime)
    run_unauthorised_tool_step(runtime)
    run_complete_topic_step(runtime)
    run_production_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Production-ready agents need deterministic controls around the model. "
        "Validation, authorisation, error handling, and observable state changes make behaviour safer and easier to debug."
    )


if __name__ == "__main__":
    main()
