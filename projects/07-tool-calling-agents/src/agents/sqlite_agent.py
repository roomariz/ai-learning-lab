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
from src.tools.tools import get_weather, calculate


SYSTEM_PROMPT = r"""You are a helpful assistant.

- Be conversational and friendly.
- If the user asks for weather with a city, use the weather tool.
- If the user asks for a calculation, use the calculator tool.
- Remember information the user tells you about themselves.
- Never mention tool names or internal execution details.
- If genuinely missing information, ask a brief clarification.
- Always respond to the user's actual question."""


def create_sqlite_agent(model_name: str = "llama3.1:latest", temperature: int = 0, db_path: str = "checkpoints.db"):
    model = ChatOllama(model=model_name, temperature=temperature)

    import sqlite3
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent, conn


def run_sqlite_demo():
    agent, conn = create_sqlite_agent()
    config = {"configurable": {"thread_id": "conversation-1"}}

    print("SQLite Agent - Type 'exit' or 'quit' to stop\n")
    print("Commands: 'clean memory' to clear conversation history\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            break

        if user_input.lower().strip() in ("clean memory", "clear memory", "forget everything"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", ("conversation-1",))
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