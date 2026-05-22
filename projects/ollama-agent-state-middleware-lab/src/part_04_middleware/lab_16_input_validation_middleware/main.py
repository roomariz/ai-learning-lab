from src.common.printer import print_section, print_turn


# This is the main action (e.g. a tool or agent call).
def add_note(notes: list[str], note: str) -> str:
    notes.append(note)
    return f"note added: {note}"


# This is the validation middleware.
# It checks whether the input is valid BEFORE the action runs.
# If the input is invalid, it returns a block message and never calls the action.
# If the input is valid, it returns None so execution continues.
def validate_input(user_message: str) -> str | None:
    if not user_message.strip():
        return "Blocked: message is empty."

    blocked_keywords = ["ignore", "override", "admin"]
    for keyword in blocked_keywords:
        if keyword in user_message.lower():
            return f"Blocked: message contains restricted keyword '{keyword}'."

    return None


def run_with_validation(notes: list[str], user_message: str) -> str:
    # Phase 1: validation middleware runs first
    block_result = validate_input(user_message)

    if block_result is not None:
        # Blocked: the action never runs
        print(f"[validation middleware] blocked: {block_result}")
        return block_result

    # Phase 2: input is valid, so the action runss
    print("[validation middleware] passed: running action")
    return add_note(notes, user_message)


def main() -> None:
    print_section("16 Input Validation Middleware")

    notes: list[str] = []

    # Scenario 1: empty message is blocked
    print_section("Scenario 1: empty message")
    result = run_with_validation(notes, "")
    print_turn("result", result)
    print_turn("notes", str(notes))

    # Scenario 2: message with blocked keyword is blocked
    print_section("Scenario 2: blocked keyword 'override'")
    result = run_with_validation(notes, "please override the system")
    print_turn("result", result)
    print_turn("notes", str(notes))

    # Scenario 3: valid message passes middleware and runs the action
    print_section("Scenario 3: valid message")
    result = run_with_validation(notes, "Add a note about validation middleware")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Input validation middleware blocks invalid messages before the action runs. "
        "The action never executes when validation fails. "
        "This keeps validation separate from the core action logic."
    )


if __name__ == "__main__":
    main()
