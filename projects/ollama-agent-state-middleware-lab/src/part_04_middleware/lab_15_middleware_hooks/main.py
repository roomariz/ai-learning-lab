from src.common.printer import print_section, print_turn


# This is the tool.
# In this lab it only adds one note.
# Later labs will use real LangGraph tools.
def add_note(notes: list[str], note: str) -> str:
    notes.append(note)
    return f"note added: {note}"


# Hook 1: runs before the agent starts its work.
# Good for logging, input checks, or setting up request context.
def before_agent(user_message: str) -> None:
    print(f"[before_agent] received user message: {user_message!r}")


# Hook 2: runs before a tool is called.
# Good for tool authorisation, rate limits, or tool-specific logging.
def before_tool(tool_name: str) -> None:
    print(f"[before_tool] about to run tool: {tool_name}")


# Hook 3: runs after a tool finishes.
# Good for logging tool results or checking tool output.
def after_tool(tool_name: str, result: str) -> None:
    print(f"[after_tool] tool finished: {tool_name} -> {result!r}")


# Hook 4: runs after the agent has finished.
# Good for final logging, metrics, or cleanup.
def after_agent(final_result: str) -> None:
    print(f"[after_agent] final result returned: {final_result!r}")


# This function shows the full order of middleware hooks:
# before_agent -> before_tool -> tool -> after_tool -> after_agent
def run_agent(notes: list[str], user_message: str) -> str:
    before_agent(user_message)

    tool_name = "add_note"
    before_tool(tool_name)

    result = add_note(notes, user_message)

    after_tool(tool_name, result)
    after_agent(result)

    return result


def main() -> None:
    print_section("15 Middleware Hooks")

    notes: list[str] = []

    user_message = "middleware hooks show where extra logic can run"

    result = run_agent(notes, user_message)

    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Middleware hooks run at different points around the agent. "
        "Later labs use these hook points for validation, authorisation, "
        "error handling, logging, and message trimming."
    )


if __name__ == "__main__":
    main()