"""
Lab 17: Tool Authorisation Middleware

This lab shows how middleware can stop an unauthorised tool
before the tool runs.
"""

from src.common.printer import print_section, print_turn


def add_note(notes: list[str], note: str) -> str:
    """Allowed tool: add one note."""
    notes.append(note)
    return f"note added: {note}"


def delete_all_notes(notes: list[str]) -> str:
    """Restricted tool: delete every note."""
    notes.clear()
    return "all notes deleted"


def authorise_tool(tool_name: str) -> str | None:
    """Return None when the tool is allowed, otherwise return a block message."""
    allowed_tools = ["add_note"]

    if tool_name not in allowed_tools:
        return f"Blocked: tool '{tool_name}' is not authorised."

    return None


def run_with_authorisation(
    notes: list[str],
    tool_name: str,
    message: str = "",
) -> str:
    """Check authorisation before running the selected tool."""
    block_result = authorise_tool(tool_name)

    if block_result is not None:
        print(f"[authorisation middleware] blocked: {block_result}")
        return block_result

    print("[authorisation middleware] passed: running tool")

    if tool_name == "add_note":
        return add_note(notes, message)

    if tool_name == "delete_all_notes":
        return delete_all_notes(notes)

    return "unknown tool"


def main() -> None:
    print_section("17 Tool Authorisation Middleware")

    notes = ["existing note"]

    print_section("Scenario 1: authorised tool")
    result = run_with_authorisation(
        notes,
        "add_note",
        "authorised tool executed",
    )
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 2: blocked tool")
    result = run_with_authorisation(notes, "delete_all_notes")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Tool authorisation middleware checks whether a tool is allowed "
        "before execution. Blocked tools never run."
    )


if __name__ == "__main__":
    main()