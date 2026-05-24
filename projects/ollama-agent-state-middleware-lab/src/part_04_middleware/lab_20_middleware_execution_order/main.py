from src.common.printer import print_section, print_turn


def add_note(notes: list[str], note: str) -> str:
    notes.append(note)
    return f"note added: {note}"


def risky_note(notes: list[str], note: str) -> str:
    raise ValueError(f"invalid note: {note}")


def delete_all(notes: list[str], note: str) -> str:
    notes.clear()
    return "all notes deleted"


class LoggingMiddleware:
    def before(self, tool_name: str, args: dict) -> bool:
        print("[logging] before")
        return True

    def after(self, tool_name: str, result: str) -> None:
        print("[logging] after")


class ErrorHandlingMiddleware:
    def before(self, tool_name: str, args: dict) -> bool:
        return True

    def error(self, tool_name: str, exc: Exception) -> None:
        print(f"[error handler] caught {type(exc).__name__}")


class AuthorisationMiddleware:
    def before(self, tool_name: str, args: dict) -> bool:
        if tool_name == "delete_all":
            print("[authorisation] blocked")
            return False
        print("[authorisation] passed")
        return True


class ValidationMiddleware:
    def before(self, tool_name: str, args: dict) -> bool:
        note = args.get("note", "")
        if not note or not note.strip():
            print("[validation] blocked")
            return False
        print("[validation] passed")
        return True


def run_pipeline(middleware_list, tool_fn, notes, note):
    args = {"note": note}
    tool_name = tool_fn.__name__

    result = f"Blocked before running {tool_name}"
    error = None
    middleware_that_ran = []

    # Step 1: run middleware before checks in order.
    for middleware in middleware_list:
        allowed = middleware.before(tool_name, args)

        if not allowed:
            # This middleware blocked the request.
            # The tool will not run.
            break

        # Only middleware that passed is added here.
        # These middleware can later run after/error logic.
        middleware_that_ran.append(middleware)

    # Step 2: if every middleware passed, run the tool.
    if len(middleware_that_ran) == len(middleware_list):
        print(f"[tool] running {tool_name}")
        try:
            result = tool_fn(notes, note)
        except Exception as caught_error:
            error = caught_error

    # Step 3: unwind in reverse order.
    # This is like walking back out through the same middleware.
    for middleware in reversed(middleware_that_ran):
        if error is not None and hasattr(middleware, "error"):
            middleware.error(tool_name, error)
        elif hasattr(middleware, "after"):
            middleware.after(tool_name, result)

    # Step 4: return either the controlled error or the result.
    if error is not None:
        return f"Error ({type(error).__name__}): {error}"

    return result


    # Run the unwind phase in reverse order.
    # Only middleware that successfully ran before the block gets an after/error phase.
    # The middleware that blocked execution does not run after(), because it stopped the chain.
    for i in range(len(middleware_list) - 1, -1, -1):
        if i >= blocker_index:
            continue
        mw = middleware_list[i]
        if error is not None and hasattr(mw, "error"):
            mw.error(tool_name, error)
        elif hasattr(mw, "after"):
            mw.after(tool_name, result)

    if error:
        return f"Error ({type(error).__name__}): {error}"
    return result


def main() -> None:
    print_section("20 Middleware Execution Order")

    middleware_stack = [
        LoggingMiddleware(),
        ErrorHandlingMiddleware(),
        ValidationMiddleware(),
        AuthorisationMiddleware(),
    ]

    notes: list[str] = []

    print_section("Scenario 1: Normal flow")
    result = run_pipeline(middleware_stack, add_note, notes, "buy groceries")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 2: Validation blocks")
    result = run_pipeline(middleware_stack, add_note, notes, "")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 3: Authorisation blocks")
    result = run_pipeline(middleware_stack, delete_all, notes, "anything")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 4: Tool crashes, error handler catches")
    result = run_pipeline(middleware_stack, risky_note, notes, "correct input")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Middleware execution order determines system behaviour.\n"
        "Validation and authorisation must run before tool execution.\n"
        "Error handling wraps risky execution, and logging wraps everything.\n"
        "Order matters. Same middleware, different order, different outcome."
    )


if __name__ == "__main__":
    main()
