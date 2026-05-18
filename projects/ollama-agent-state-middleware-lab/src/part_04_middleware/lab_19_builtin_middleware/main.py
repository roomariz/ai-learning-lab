from dataclasses import dataclass, field
from typing import Callable, TypedDict


class BuiltinMiddlewareState(TypedDict):
    learner_name: str
    current_topic: str
    completed_topics: list[str]
    last_action: str
    notes: list[str]
    middleware_log: list[str]


@dataclass
class BuiltinMiddleware:
    name: str
    before_model: Callable[[dict, "BuiltinRuntime"], None] | None = None
    after_model: Callable[[dict, "BuiltinRuntime"], None] | None = None


@dataclass
class BuiltinRuntime:
    context: dict
    middleware_stack: list[BuiltinMiddleware] = field(default_factory=list)

    def execute(self, state: dict) -> None:
        for mw in self.middleware_stack:
            if mw.before_model:
                mw.before_model(state, self)
                state["middleware_log"].append(f"{mw.name}.before_model")

        state["middleware_log"].append("[model call]")

        for mw in reversed(self.middleware_stack):
            if mw.after_model:
                mw.after_model(state, self)
                state["middleware_log"].append(f"{mw.name}.after_model")


def create_builtin_middleware_demo() -> None:
    request_id_middleware = BuiltinMiddleware(
        name="request_id",
        before_model=lambda s, r: print("[request_id] Generating request ID for turn."),
        after_model=lambda s, r: print("[request_id] Request completed."),
    )

    timing_middleware = BuiltinMiddleware(
        name="timing",
        before_model=lambda s, r: print("[timing] Model call starting."),
        after_model=lambda s, r: print("[timing] Model call finished."),
    )

    print(
        "This lab demonstrates built-in middleware hooks.\n"
        "It shows where before_model and after_model run in the agent lifecycle."
    )

    print("\nMiddleware registered:")
    print("  1. request_id  - logs request ID generation")
    print("  2. timing      - logs model call timing")

    print("\nHook execution order:")
    print("  before_model hooks run before the LLM call.")
    print("  after_model hooks run after the LLM call.")
    print("  Middleware runs in the order they are registered.")

    print("\n" + "-" * 40)
    print("Demo execution:")

    runtime = BuiltinRuntime(context={})
    runtime.middleware_stack = [request_id_middleware, timing_middleware]

    state: BuiltinMiddlewareState = {
        "learner_name": "Muhammad",
        "current_topic": "builtin_middleware",
        "completed_topics": [],
        "last_action": "started_builtin_middleware",
        "notes": [],
        "middleware_log": [],
    }

    runtime.execute(state)


def main() -> None:
    print("19 Built-in Middleware")
    print("=" * 40)

    create_builtin_middleware_demo()

    print("\nConclusion")
    print("-" * 40)
    print(
        "Built-in middleware hooks: before_model and after_model. "
        "These allow you to inject logic at the start and end of each model call. "
        "Common uses include request ID generation, timing, logging, and metrics collection."
    )


if __name__ == "__main__":
    main()