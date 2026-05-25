from langchain.tools import tool


@tool
def explain_topic(topic: str) -> str:
    """Explain a learning topic in simple terms."""
    return f"{topic}: explanation with simple concepts and examples."


@tool
def generate_practice_question(topic: str) -> str:
    """Generate one practical coding question for the given topic."""
    return (
        f"Practice question for {topic}: "
        "Write a decorator called `log_call` that prints the wrapped function's "
        "name before calling it. Apply it to a function called `add(a, b)` and "
        "show the expected output."
    )


@tool
def grade_answer(question: str, student_answer: str) -> str:
    """Grade a student's answer."""
    return f"Feedback for '{question}': good attempt, but more detail is needed."


@tool
def create_study_plan(subject: str, days: int) -> str:
    """Create a study plan."""
    return f"Created a {days}-day study plan for {subject}."


@tool
def broken_quiz_generator(topic: str) -> str:
    """Simulate a failing quiz generation service."""
    raise RuntimeError("Quiz service is temporarily unavailable")
