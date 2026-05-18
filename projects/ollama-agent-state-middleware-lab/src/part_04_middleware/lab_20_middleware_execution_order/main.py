from dataclasses import dataclass, field
from typing import Callable, TypedDict


class MiddlewareState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    execution_log: list[str]


@dataclass
class Middleware:
    name: str
    before_model: Callable[[dict, "Runtime"], None] | None = None
    after_model: Callable[[dict, "Runtime"], None] | None = None
    before_tool: Callable[[dict, "Runtime"], None] | None = None
    after_tool: Callable[[dict, "Runtime"], None] | None = None


@dataclass
class Runtime:
    context: dict
    middleware_stack: list[Middleware] = field(default_factory=list)

    def execute_with_middleware(self, state: dict) -> None:
        execution_log: list[str] = []

        before_model_middlewares = [
            m for m in self.middleware_stack if m.before_model
        ]
        after_model_middlewares = [
            m for m in reversed(self.middleware_stack) if m.after_model
        ]

        for mw in before_model_middlewares:
            if mw.before_model:
                mw.before_model(state, self)
                execution_log.append(f"{mw.name}.before_model")

        execution_log.append("[model call]")

        for mw in after_model_middlewares:
            if mw.after_model:
                mw.after_model(state, self)
                execution_log.append(f"{mw.name}.after_model")

        state["execution_log"] = execution_log


def main() -> None:
    print("20 Middleware Execution Order")
    print("=" * 40)
    print(
        "This lab demonstrates the execution order of multiple middleware instances.\n"
        "before_model hooks run in registration order.\n"
        "after_model hooks run in reverse registration order.\n"
    )

    middleware_a = Middleware(
        name="MiddlewareA",
        before_model=lambda s, r: print("[A] before_model"),
        after_model=lambda s, r: print("[A] after_model"),
    )

    middleware_b = Middleware(
        name="MiddlewareB",
        before_model=lambda s, r: print("[B] before_model"),
        after_model=lambda s, r: print("[B] after_model"),
    )

    print("Middleware registered: [A, B]")
    print("Expected order:")
    print("  [A] before_model")
    print("  [B] before_model")
    print("  [model call]")
    print("  [B] after_model")
    print("  [A] after_model")
    print()
    print("-" * 40)

    runtime = Runtime(context={"user_id": "learner-001"})
    runtime.middleware_stack = [middleware_a, middleware_b]

    state: MiddlewareState = {
        "learner_name": "Muhammad",
        "current_topic": "middleware_execution_order",
        "completed_topics": [
            "production_ready_agents",
            "middleware_concept",
            "middleware_hooks",
            "input_validation_middleware",
            "tool_authorisation",
            "error_handling_middleware",
            "builtin_middleware",
        ],
        "last_action": "started_middleware_execution_order",
        "notes": [],
        "execution_log": [],
    }

    runtime.execute_with_middleware(state)

    print("-" * 40)
    print("\nExecution log:")
    for entry in state["execution_log"]:
        print(f"  {entry}")

    print("\nConclusion")
    print("-" * 40)
    print(
        "Middleware execution follows a predictable nesting pattern. "
        "before_model runs in registration order; after_model runs in reverse. "
        "This allows middleware to wrap the model call cleanly."
    )


if __name__ == "__main__":
    main()