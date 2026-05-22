from src.common.printer import print_section, print_turn


def before_model(user_message: str) -> str:
    """Built-in-style hook that runs before the model.

    In real framework middleware, this hook can inspect or modify the message
    before the model receives it.
    """
    print("[before_model] inspecting user message")
    return user_message.strip()


def call_model(user_message: str) -> str:
    """Tiny fake model used to keep this lab deterministic.

    Later labs can replace this with a real LangGraph agent/model call.
    """
    if "note" in user_message.lower():
        return "tool:add_note"
    return "no_tool"


def add_note(notes: list[str], note: str) -> str:
    """Tool called by the fake model decision."""
    notes.append(note)
    return f"note added: {note}"


def wrap_tool_call(tool_name: str, notes: list[str], note: str) -> str:
    """Built-in-style hook that wraps tool execution.

    In real framework middleware, this is where you can log, authorise,
    catch errors, or measure tool execution.
    """
    print(f"[wrap_tool_call] running tool: {tool_name}")

    if tool_name == "add_note":
        return add_note(notes, note)

    return f"unknown tool: {tool_name}"


def after_model(model_decision: str) -> None:
    """Built-in-style hook that runs after the model.

    In real framework middleware, this hook can inspect the model output,
    record metrics, or apply response checks.
    """
    print(f"[after_model] model decision: {model_decision}")


def run_agent(notes: list[str], user_message: str) -> str:
    cleaned_message = before_model(user_message)

    model_decision = call_model(cleaned_message)

    after_model(model_decision)

    if model_decision == "tool:add_note":
        return wrap_tool_call("add_note", notes, cleaned_message)

    return "no tool was needed"


def main() -> None:
    print_section("19 Built-in Middleware")

    notes: list[str] = []

    print_section("Scenario 1: message uses a tool")
    result = run_agent(notes, "  Add a note about built-in middleware  ")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Scenario 2: message does not need a tool")
    result = run_agent(notes, "hello")
    print_turn("result", result)
    print_turn("notes", str(notes))

    print_section("Conclusion")
    print()
    print(
        "Built-in middleware gives frameworks standard hook points such as "
        "before_model, wrap_tool_call, and after_model. Earlier labs built "
        "the idea manually. This lab shows how those ideas map to framework-style hooks."
    )


if __name__ == "__main__":
    main()