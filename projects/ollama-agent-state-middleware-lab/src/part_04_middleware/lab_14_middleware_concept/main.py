from src.common.printer import print_section, print_turn


# This is the main action.
# In later labs, this could be an agent call or a tool call.
# For now, it only adds a note so the middleware idea is easy to see.
def add_note(notes: list[str], note: str) -> str:
    notes.append(note)
    return f"note added: {note}"


# This represents code that runs BEFORE the main action.
# It does not change anything yet. It only observes and prints what is about to run.
def middleware_before(action: str) -> None:
    print(f"[middleware before] about to run: {action}")


# This represents code that runs AFTER the main action.
# It does not change anything yet. It only observes and prints what has finished.
def middleware_after(action: str) -> None:
    print(f"[middleware after] finished running: {action}")


def main() -> None:
    print_section("14 Middleware Concept")

    # Shared state for this tiny demo.
    # Later labs will use AgentState instead.
    notes: list[str] = []

    # First, run the action directly.
    # There is no middleware, so only add_note runs.
    print_section("Without middleware")
    result = add_note(notes, "middleware runs around agent work")
    print_turn("result", result)
    print_turn("notes", str(notes))

    # Now run the same kind of action with middleware around it.
    # The order is:
    # 1. middleware_before
    # 2. add_note
    # 3. middleware_after
    print_section("With middleware")
    middleware_before("add_note")
    result = add_note(notes, "middleware can observe what happens")
    middleware_after("add_note")

    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Middleware is code that runs around the main work. "
        "It can observe what happens before and after an action. "
        "Later labs use real LangGraph middleware."
    )


if __name__ == "__main__":
    main()