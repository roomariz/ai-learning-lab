import json
from dataclasses import dataclass
from typing import TypedDict

from src.common.printer import print_section, print_turn


class AuthState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    auth_check_count: int
    auth_blocked_count: int
    auth_log: list[str]


class AuthContext(TypedDict):
    user_id: str
    role: str
    environment: str
    authorised_tools: list[str]
    role_permissions: dict[str, list[str]]
    admin_tools: list[str]


class Request(TypedDict):
    user_message: str
    tool_name: str
    payload: str


@dataclass
class AuthRuntime:
    state: AuthState
    context: AuthContext

    def log_auth(self, message: str) -> None:
        self.state["auth_log"].append(message)

    def record_auth_check(self) -> None:
        self.state["auth_check_count"] += 1

    def record_auth_blocked(self) -> None:
        self.state["auth_blocked_count"] += 1

    def record_action(self, action: str) -> None:
        self.state["last_action"] = action


class ToolAuthorisationMiddleware:
    def __init__(self, runtime: AuthRuntime) -> None:
        self.runtime = runtime

    def check_tool_allowed(self, tool_name: str) -> str | None:
        self.runtime.record_auth_check()
        self.runtime.log_auth(f"auth_check: {tool_name}")

        if tool_name in self.runtime.context["admin_tools"]:
            if self.runtime.context["role"] != "admin":
                self.runtime.record_auth_blocked()
                self.runtime.record_action(f"blocked_admin_tool:{tool_name}")
                self.runtime.log_auth(f"blocked: admin-only tool for role '{self.runtime.context['role']}'")
                return f"Blocked: {tool_name} requires admin role."

        if tool_name not in self.runtime.context["authorised_tools"]:
            self.runtime.record_auth_blocked()
            self.runtime.record_action(f"blocked_tool:{tool_name}")
            self.runtime.log_auth(f"blocked: tool not in authorised_tools")
            return f"Blocked: {tool_name} is not authorised."

        self.runtime.log_auth(f"allowed: {tool_name}")
        return None

    def check_role_permission(self, tool_name: str) -> str | None:
        role = self.runtime.context["role"]
        role_perms = self.runtime.context["role_permissions"]

        if role not in role_perms:
            self.runtime.record_auth_blocked()
            self.runtime.log_auth(f"blocked: no permissions defined for role '{role}'")
            return f"Blocked: role '{role}' has no defined permissions."

        allowed = role_perms[role]
        if tool_name not in allowed:
            self.runtime.record_auth_blocked()
            self.runtime.log_auth(f"blocked: tool '{tool_name}' not in role permissions for '{role}'")
            return f"Blocked: {tool_name} is not permitted for role '{role}'."

        self.runtime.log_auth(f"role_allowed: {tool_name} for role '{role}'")
        return None


def create_state() -> AuthState:
    return {
        "learner_name": "Muhammad",
        "current_topic": "tool_authorisation",
        "completed_topics": [
            "production_ready_agents",
            "middleware_concept",
            "middleware_hooks",
            "input_validation_middleware",
        ],
        "last_action": "started_tool_authorisation_lab",
        "notes": [],
        "auth_check_count": 0,
        "auth_blocked_count": 0,
        "auth_log": [],
    }


def create_context() -> AuthContext:
    return {
        "user_id": "learner-001",
        "role": "learner",
        "environment": "local",
        "authorised_tools": [
            "add_note",
            "complete_topic",
            "list_progress",
        ],
        "admin_tools": [
            "delete_all_notes",
            "reset_progress",
            "update_user_role",
        ],
        "role_permissions": {
            "learner": ["add_note", "complete_topic", "list_progress"],
            "admin": [
                "add_note",
                "complete_topic",
                "list_progress",
                "delete_all_notes",
                "reset_progress",
                "update_user_role",
            ],
            "moderator": [
                "add_note",
                "complete_topic",
                "list_progress",
                "delete_all_notes",
            ],
        },
    }


def format_json(data: AuthState | AuthContext) -> str:
    return json.dumps(data, indent=2)


def run_check_allowed_blocked_tool(runtime: AuthRuntime) -> None:
    middleware = ToolAuthorisationMiddleware(runtime)

    result = middleware.check_tool_allowed("delete_all_notes")

    print_section("Step 1: admin tool blocked for learner role")
    print_turn("tool", "delete_all_notes")
    print_turn("role", runtime.context["role"])
    print_turn("result", result or "allowed")


def run_check_allowed_authorised_tool(runtime: AuthRuntime) -> None:
    middleware = ToolAuthorisationMiddleware(runtime)

    result = middleware.check_tool_allowed("add_note")

    print_section("Step 2: authorised tool allowed")
    print_turn("tool", "add_note")
    print_turn("role", runtime.context["role"])
    print_turn("result", result or "allowed")


def run_check_allowed_unknown_tool(runtime: AuthRuntime) -> None:
    middleware = ToolAuthorisationMiddleware(runtime)

    result = middleware.check_tool_allowed("update_config")

    print_section("Step 3: unknown tool blocked")
    print_turn("tool", "update_config")
    print_turn("role", runtime.context["role"])
    print_turn("result", result or "allowed")


def run_role_permission_learner(runtime: AuthRuntime) -> None:
    middleware = ToolAuthorisationMiddleware(runtime)

    result = middleware.check_role_permission("delete_all_notes")

    print_section("Step 4: role permission check (learner blocked)")
    print_turn("tool", "delete_all_notes")
    print_turn("role", "learner")
    print_turn("result", result or "allowed")


def run_role_permission_admin(runtime: AuthRuntime) -> None:
    runtime.context["role"] = "admin"
    middleware = ToolAuthorisationMiddleware(runtime)

    result = middleware.check_role_permission("delete_all_notes")

    print_section("Step 5: role permission check (admin allowed)")
    print_turn("tool", "delete_all_notes")
    print_turn("role", "admin")
    print_turn("result", result or "allowed")

    runtime.context["role"] = "learner"


def run_auth_summary(runtime: AuthRuntime) -> None:
    summary = (
        "Tool authorisation middleware checks if a user or role can run a tool.\n"
        f"Auth checks performed: {runtime.state['auth_check_count']}\n"
        f"Auth blocks: {runtime.state['auth_blocked_count']}\n"
        "Checks: tool in authorised list, tool not admin-only, tool in role permissions."
    )

    print_section("Authorisation summary")
    print_turn("summary", summary)
    print_turn("auth log", format_json(runtime.state["auth_log"]))
    print_turn("final state", format_json(runtime.state))


def main() -> None:
    print_section("17 Tool Authorisation")

    state = create_state()
    context = create_context()
    runtime = AuthRuntime(state=state, context=context)

    print_turn("initial context", format_json(context))

    run_check_allowed_blocked_tool(runtime)
    run_check_allowed_authorised_tool(runtime)
    run_check_allowed_unknown_tool(runtime)
    run_role_permission_learner(runtime)
    run_role_permission_admin(runtime)
    run_auth_summary(runtime)

    print_section("Conclusion")
    print()
    print(
        "Tool authorisation middleware ensures users can only run tools they are permitted to use. "
        "It checks the tool against an authorised list, admin restrictions, and role-based permissions."
    )


if __name__ == "__main__":
    main()