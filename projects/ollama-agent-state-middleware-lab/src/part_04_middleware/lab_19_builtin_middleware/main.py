from langchain.agents import create_agent
from langchain.agents.middleware import create_middleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from src.common.model import get_chat_model


def create_builtin_middleware_demo() -> None:
    model = get_chat_model()

    request_id_middleware = create_middleware(
        name="request_id",
        before_model=lambda state, runtime: print(
            f"[request_id] Generating request ID for turn."
        ),
        after_model=lambda state, runtime: print(
            f"[request_id] Request completed."
        ),
    )

    timing_middleware = create_middleware(
        name="timing",
        before_model=lambda state, runtime: print(
            f"[timing] Model call starting."
        ),
        after_model=lambda state, runtime: print(
            f"[timing] Model call finished."
        ),
    )

    print(
        "This lab demonstrates LangGraph's built-in middleware hooks.\n"
        "It shows where before_model and after_model run in the agent lifecycle."
    )

    print("\nMiddleware registered:")
    print("  1. request_id  - logs request ID generation")
    print("  2. timing      - logs model call timing")

    print("\nHook execution order:")
    print("  before_model hooks run before the LLM call.")
    print("  after_model hooks run after the LLM call.")
    print("  Middleware runs in the order they are registered.")


def create_agent_with_middleware() -> None:
    model = get_chat_model()

    request_id_middleware = create_middleware(
        name="request_id",
        before_model=lambda state, runtime: print("[request_id] start"),
        after_model=lambda state, runtime: print("[request_id] end"),
    )

    timing_middleware = create_middleware(
        name="timing",
        before_model=lambda state, runtime: print("[timing] start"),
        after_model=lambda state, runtime: print("[timing] end"),
    )

    print("\nCreating agent with middleware pipeline...")

    agent = create_agent(
        model=model,
        tools=[],
        middleware=[request_id_middleware, timing_middleware],
    )

    print("Agent created. Invoking with a test message...")

    result = agent.invoke({
        "messages": [HumanMessage(content="Say hello in one word.")]
    })

    print("\nAgent invocation complete.")
    print(f"Response: {result['messages'][-1].content}")


def main() -> None:
    print("19 Built-in Middleware")
    print("=" * 40)

    create_builtin_middleware_demo()
    create_agent_with_middleware()

    print("\nConclusion")
    print("-" * 40)
    print(
        "LangGraph provides built-in middleware hooks: before_model and after_model. "
        "These allow you to inject logic at the start and end of each model call. "
        "Common uses include request ID generation, timing, logging, and metrics collection."
    )


if __name__ == "__main__":
    main()