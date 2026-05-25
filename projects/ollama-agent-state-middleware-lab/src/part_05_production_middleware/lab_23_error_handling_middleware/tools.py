from langchain.tools import tool


@tool
def broken_quiz_generator(topic: str) -> str:
    """Simulate a failing quiz generation service."""
    raise RuntimeError("Quiz service is temporarily unavailable")

