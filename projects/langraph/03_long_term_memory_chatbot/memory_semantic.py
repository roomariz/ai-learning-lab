import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langgraph.store.memory import InMemoryStore


load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    raise RuntimeError("COHERE_API_KEY is missing. Add it to your .env file.")


embeddings = CohereEmbeddings(
    model="embed-english-v3.0",
    cohere_api_key=cohere_api_key,
)

store = InMemoryStore(
    index={
        "embed": embeddings,
        "dims": 1024,
        "fields": ["memory_text"],
    }
)


def memory_namespace(user_id: str) -> tuple[str, str]:
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required")

    return ("memories", user_id)


def add_memory(user_id: str, memory_text: str) -> None:
    if not memory_text or not memory_text.strip():
        raise ValueError("memory_text is required")

    store.put(
        memory_namespace(user_id),
        str(uuid4()),
        {"memory_text": memory_text},
        index=["memory_text"],
    )


def search_memories(user_id: str, user_message: str, limit: int = 5) -> list[str]:
    if not user_message or not user_message.strip():
        return []

    results = store.search(
        memory_namespace(user_id),
        query=user_message,
        limit=limit,
    )

    return [item.value["memory_text"] for item in results]


def list_memories(user_id: str, limit: int = 100) -> list[tuple[str, str]]:
    results = store.search(
        memory_namespace(user_id),
        limit=limit,
    )

    return [
        (item.key, item.value["memory_text"])
        for item in results
    ]


def delete_memory(user_id: str, memory_id: str) -> None:
    store.delete(
        memory_namespace(user_id),
        memory_id,
    )


def delete_all_memories(user_id: str) -> None:
    for memory_id, _ in list_memories(user_id):
        delete_memory(user_id, memory_id)