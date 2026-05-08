"""
SQLite-backed agent implementation.

This module creates an LLM agent that can:
- call registered tools
- persist conversation state in SQLite
- resume previous sessions
- support evaluation scenarios

Use this when you want memory across runs.
"""

import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langgraph.checkpoint.base")

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.tools.tool_registry import get_weather, calculate

DEFAULT_MODEL = "llama3.1:latest"
DETERMINISTIC_TEMPERATURE = 0
DEFAULT_DB_PATH = "checkpoints.db"
DEFAULT_THREAD_ID = "conversation-1"

SYSTEM_PROMPT = r"""You are a helpful assistant.

- Be conversational and friendly.
- If the user asks for weather with a city, use the weather tool.
- If the user asks for a calculation, use the calculator tool.
- Remember information the user tells you about themselves.
- Never mention tool names or internal execution details.
- If genuinely missing information, ask a brief clarification.
- Always respond to the user's actual question."""


def create_sqlite_agent(
    model_name: str = DEFAULT_MODEL,
    temperature: int = DETERMINISTIC_TEMPERATURE,
    db_path: str = DEFAULT_DB_PATH,
):
    """
    Create an agent with persistent SQLite-backed memory.

    The agent stores conversation checkpoints so state survives
    process restarts. Use this for long-running sessions that need
    to resume after restarts.

    Args:
        model_name:
            Name of the LLM model to use (e.g., "llama3.1:latest").
        temperature:
            Sampling temperature (0 for deterministic output).
        db_path:
            Path to SQLite database for checkpoint persistence.

    Returns:
        A tuple of (agent, database_connection).
    """
    model = ChatOllama(model=model_name, temperature=temperature)

    import sqlite3

    # Persist conversation checkpoints to SQLite so the agent can resume
    # context between independent executions.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent, conn


def run_sqlite_demo() -> None:
    """
    Run an interactive demo of the SQLite-backed agent.

    Provides a console interface where users can:
    - Chat with the agent (uses persisted memory)
    - Clear memory with 'clean memory' command
    - Exit with 'exit' or 'quit'

    The agent remembers conversation history within each thread.
    """
    agent, conn = create_sqlite_agent()
    config = {"configurable": {"thread_id": DEFAULT_THREAD_ID}}

    print("SQLite Agent - Type 'exit' or 'quit' to stop\n")
    print("Commands: 'clean memory' to clear conversation history\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            break

        if user_input.lower().strip() in ("clean memory", "clear memory", "forget everything"):
            # Clear checkpoints for this thread to start fresh conversation.
            cursor = conn.cursor()
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (DEFAULT_THREAD_ID,))
            conn.commit()
            print("Assistant: Memory cleared. Starting fresh!\n")
            continue

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        print(f"Assistant: {response['messages'][-1].content}\n")


if __name__ == "__main__":
    run_sqlite_demo()