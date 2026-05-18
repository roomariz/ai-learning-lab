from langchain.agents import create_agent
from langchain.agents.middleware import create_middleware
from langchain_core.messages import HumanMessage

from src.common.model import get_chat_model


def main() -> None:
    print("20 Middleware Execution Order")
    print("=" * 40)
    print(
        "This lab demonstrates the execution order of multiple middleware instances.\n"
        "before_model hooks run in registration order.\n"
        "after_model hooks run in reverse registration order.\n"
    )

    middleware_a = create_middleware(
        name="MiddlewareA",
        before_model=lambda state, runtime: print("[A] before_model"),
        after_model=lambda state, runtime: print("[A] after_model"),
    )

    middleware_b = create_middleware(
        name="MiddlewareB",
        before_model=lambda state, runtime: print("[B] before_model"),
        after_model=lambda state, runtime: print("[B] after_model"),
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

    model = get_chat_model()
    agent = create_agent(
        model=model,
        tools=[],
        middleware=[middleware_a, middleware_b],
    )

    result = agent.invoke({
        "messages": [HumanMessage(content="Say hello in one word.")]
    })

    print("-" * 40)
    print("\nAgent response:", result["messages"][-1].content)

    print("\nConclusion")
    print("-" * 40)
    print(
        "Middleware execution follows a predictable nesting pattern. "
        "before_model runs in registration order; after_model runs in reverse. "
        "This allows middleware to wrap the model call cleanly."
    )


if __name__ == "__main__":
    main()