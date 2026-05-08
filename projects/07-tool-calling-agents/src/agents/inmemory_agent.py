"""
In-memory agent implementation.

This module creates an LLM agent that can:
- call registered tools
- maintain conversation state in runtime memory
- support evaluation scenarios

Use this for stateless sessions or when persistence is not needed.
"""

import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langgraph.checkpoint.base")

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.tools.tool_registry import get_weather, calculate

DEFAULT_MODEL = "llama3.1:latest"
DETERMINISTIC_TEMPERATURE = 0
DEFAULT_THREAD_ID = "conversation-1"

SYSTEM_PROMPT = r"""You are a helpful assistant.

- Be conversational and friendly.
- If the user asks for weather with a city, use the weather tool.
- If the user asks for a calculation, use the calculator tool.
- Remember information the user tells you about themselves.
- Never mention tool names or internal execution details.
- If genuinely missing information, ask a brief clarification.
- Always respond to the user's actual question."""


def create_inmemory_agent(
    model_name: str = DEFAULT_MODEL,
    temperature: int = DETERMINISTIC_TEMPERATURE,
):
    """
    Create an agent with in-memory checkpoint storage.

    The agent stores conversation checkpoints in memory (RAM) for the
    duration of the process. Use this for short-lived sessions or
    when persistence is not required.

    Args:
        model_name:
            Name of the LLM model to use (e.g., "llama3.1:latest").
        temperature:
            Sampling temperature (0 for deterministic output).

    Returns:
        Configured LangGraph agent instance.
    """
    model = ChatOllama(model=model_name, temperature=temperature)

    # In-memory checkpointer persists state only within current process.
    checkpointer = MemorySaver()

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent


def run_inmemory_demo() -> None:
    """
    Run an interactive demo of the in-memory agent.

    Provides a console interface where users can chat with the agent.
    Memory is cleared when the process exits.
    """
    agent = create_inmemory_agent()
    config = {"configurable": {"thread_id": DEFAULT_THREAD_ID}}

    print("InMemory Agent - Type 'exit' or 'quit' to stop\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            break

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        print(f"Assistant: {response['messages'][-1].content}\n")


if __name__ == "__main__":
    run_inmemory_demo()