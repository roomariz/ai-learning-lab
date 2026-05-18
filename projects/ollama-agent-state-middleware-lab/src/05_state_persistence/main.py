import json
from pathlib import Path
from typing import TypedDict, cast

from langchain_ollama import ChatOllama

from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn
from src.common.utils import load_json_file, save_json_file


class PersistentLearningState(TypedDict):
    learner_name: str | None
    preferred_language: str | None
    completed_topics: list[str]
    current_topic: str | None
    last_action: str | None


STATE_FILE = Path("data/state/learning_state.json")


def format_state(state: PersistentLearningState) -> str:
    return json.dumps(state, indent=2)


def create_initial_state() -> PersistentLearningState:
    return {
        "learner_name": None,
        "preferred_language": None,
        "completed_topics": [],
        "current_topic": None,
        "last_action": None,
    }


def load_state() -> PersistentLearningState:
    saved_state = load_json_file(STATE_FILE)

    if saved_state is None:
        return create_initial_state()

    return cast(PersistentLearningState, saved_state)


def save_state(state: PersistentLearningState) -> None:
    save_json_file(STATE_FILE, dict(state))


def update_state_for_lab_05(
    state: PersistentLearningState,
) -> PersistentLearningState:
    state["learner_name"] = "Muhammad"
    state["preferred_language"] = "Python"

    if "custom_state" not in state["completed_topics"]:
        state["completed_topics"].append("custom_state")

    state["current_topic"] = "state_persistence"
    state["last_action"] = "saved_state_to_disk"

    return state


def run_first_step(model: ChatOllama, state: PersistentLearningState) -> PersistentLearningState:
    user_message = (
        "I have completed the custom state lab. "
        "Now I want to learn state persistence."
    )

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Reply in one short sentence. "
            "Acknowledge the completed topic and next topic only.",
        ),
        (
            "human",
            user_message,
        ),
    ]

    response = model.invoke(messages)

    state = update_state_for_lab_05(state)
    save_state(state)

    print_section("Step 1: update and save state")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("saved state", format_state(state))
    print_turn("state file", STATE_FILE.as_posix())

    return state


def run_second_step(model: ChatOllama) -> None:
    loaded_state = load_state()

    user_message = "What did you load from persisted state?"

    state_summary = (
        f"learner_name={loaded_state['learner_name']}\n"
        f"preferred_language={loaded_state['preferred_language']}\n"
        f"completed_topics={loaded_state['completed_topics']}\n"
        f"current_topic={loaded_state['current_topic']}\n"
        f"last_action={loaded_state['last_action']}"
    )

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Use only the loaded persisted state. "
            "Do not invent facts.",
        ),
        (
            "human",
            (
                f"Loaded persisted state:\n{state_summary}\n\n"
                f"User question: {user_message}"
            ),
        ),
    ]

    response = model.invoke(messages)

    print_section("Step 2: load state in a later step")
    print_turn("user", user_message)
    print_turn("assistant", response.content)
    print_turn("loaded state", format_state(loaded_state))


def main() -> None:
    print_section("05 State Persistence")

    model = get_chat_model()

    state = load_state()
    print_turn("initial state", format_state(state))

    state = run_first_step(model, state)
    run_second_step(model)

    print_section("Conclusion")
    print()
    print(
        "State persistence lets the program save structured state outside the model call. "
        "A later step can load that state again instead of relying on message history."
    )


if __name__ == "__main__":
    main()