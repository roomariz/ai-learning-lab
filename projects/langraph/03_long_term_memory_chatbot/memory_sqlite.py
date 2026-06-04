import sqlite3
from pathlib import Path

DB_FILE = Path("memories.db")


def setup_memory_store() -> None:
    """Ensure the memory table is available before the app starts."""
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_text TEXT NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_memory(user_id: str, memory_text: str) -> None:
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(
            "INSERT INTO user_memories (user_id, memory_text) VALUES (?, ?)",
            (user_id, memory_text),
        )


def load_memories(user_id: str) -> list[str]:
    with sqlite3.connect(DB_FILE) as connection:
        result = connection.execute(
            """
            SELECT memory_text
            FROM user_memories
            WHERE user_id = ?
            ORDER BY saved_at ASC
            """,
            (user_id,),
        ).fetchall()

    return [item[0] for item in result]

