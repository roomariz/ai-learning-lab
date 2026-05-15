from agent import create_energy_agent
from tracing import log_agent_trace


def main() -> None:
    agent = create_energy_agent()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Compare the UK's wind generation with its solar generation. "
                        "Calculate the ratio as wind generation divided by solar generation."
                    ),
                }
            ]
        }
    )

    trace_id = log_agent_trace(result, redact_content=False)

    print("\nFinal answer:")
    print(result["messages"][-1].content)

    print(f"\nLocal trace ID: {trace_id}")


if __name__ == "__main__":
    main()