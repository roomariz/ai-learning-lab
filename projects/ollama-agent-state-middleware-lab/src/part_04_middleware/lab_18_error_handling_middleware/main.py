from src.common.printer import print_section, print_turn


def safe_note(notes: list[str], note: str) -> str:
    notes.append(note)
    return f"note added: {note}"


def risky_note(notes: list[str], note: str) -> str:
    raise ValueError(f"invalid note: {note}")


def handle_error(tool_name: str, error: Exception) -> str:
    error_type = type(error).__name__
    return f"Error in {tool_name} ({error_type}): {error}"


def run_with_error_handling(notes: list[str], tool_name: str, note: str) -> str:
    if tool_name == "safe_note":
        tool = safe_note
    elif tool_name == "risky_note":
        tool = risky_note
    else:
        return f"Error: unknown tool '{tool_name}'"

    try:
        # tool is a variable that points to the selected function.
        # If tool_name is "safe_note", this calls safe_note(notes, note).
        # If tool_name is "risky_note", this calls risky_note(notes, note).
        # This keeps the error handling in one place instead of repeating try/except twice.
        return tool(notes, note)
    except Exception as error:
        error_type = type(error).__name__
        print(f"[error handling middleware] caught: {error_type}")
        return handle_error(tool_name, error)


def main() -> None:
    print_section("18 Error Handling Middleware")

    notes: list[str] = []

    print_section("Scenario 1: safe_note succeeds")
    result = run_with_error_handling(notes, "safe_note", "learning about middleware")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 2: risky_note raises ValueError")
    result = run_with_error_handling(notes, "risky_note", "bad data")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 3: unknown tool")
    result = run_with_error_handling(notes, "unknown_tool", "anything")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Error handling middleware catches exceptions from tools "
        "and returns a controlled message. The agent loop can continue "
        "instead of crashing."
    )


if __name__ == "__main__":
    main()