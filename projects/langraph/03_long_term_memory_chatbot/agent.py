import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain_cohere import ChatCohere
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver

from memory_semantic import search_memories


THREAD_DB = "threads.db"


def create_llm() -> ChatCohere:
    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        raise RuntimeError("COHERE_API_KEY is missing. Add it to your .env file.")

    return ChatCohere(
        model="command-a-03-2025",
        cohere_api_key=api_key,
    )


thread_connection = sqlite3.connect(THREAD_DB, check_same_thread=False)
checkpoint_store = SqliteSaver(thread_connection)
checkpoint_store.setup()


def memory_tool_for(user_id: str):
    @tool
    def propose_memory(fact: str) -> str:
        """Propose useful long-term information about the current user."""
        return f"PROPOSE_MEMORY::{fact}"

    return propose_memory


def create_memory_agent(user_id: str, user_message: str):
    saved_memories = search_memories(user_id, user_message, limit=5)

    memory_section = (
        "\n".join(f"- {memory}" for memory in saved_memories)
        if saved_memories
        else "No relevant saved memories found."
    )

    prompt = f"""
You are a helpful chatbot with long-term memory.

Relevant saved information about this user:
{memory_section}

Whenever the user shares a personal preference, goal, habit, location,
dietary need, allergy, name, or anything they ask you to remember,
use the propose_memory tool before responding.

Do not claim that something has been remembered unless the user approves it.
""".strip()

    return create_agent(
        model=create_llm(),
        tools=[memory_tool_for(user_id)],
        system_prompt=prompt,
        checkpointer=checkpoint_store,
    )

def summarise_thread(thread_id: str) -> str:
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    checkpoints = list(checkpoint_store.list(config))

    if not checkpoints:
        return "Empty conversation"

    latest = checkpoints[0]
    messages = latest.checkpoint.get("channel_values", {}).get("messages", [])

    if not messages:
        return "Empty conversation"

    text = "\n".join(
        f"{getattr(message, 'type', 'message')}: {getattr(message, 'content', '')}"
        for message in messages
        if getattr(message, "content", "")
    )

    if not text.strip():
        return "Empty conversation"

    llm = create_llm()

    response = llm.invoke(
        [
            {
                "role": "system",
                "content": (
                    "Summarise this chat as a short sidebar label. "
                    "Use no more than six words. No punctuation."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ]
    )

    return response.content.strip() or "Untitled conversation"

def load_thread_messages(thread_id: str) -> list[dict[str, str]]:
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    checkpoints = list(checkpoint_store.list(config))

    if not checkpoints:
        return []

    latest = checkpoints[0]
    messages = latest.checkpoint.get("channel_values", {}).get("messages", [])

    chat_history = []

    for message in messages:
        role = getattr(message, "type", "")
        content = getattr(message, "content", "")

        if not content:
            continue

        if role == "human":
            role = "user"
        elif role == "ai":
            role = "assistant"
        else:
            continue

        chat_history.append(
            {
                "role": role,
                "content": content,
            }
        )

    return chat_history