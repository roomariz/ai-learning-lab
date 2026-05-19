from langchain_ollama import ChatOllama

from src.common.config import load_config
from src.common.model import get_chat_model
from src.common.printer import print_section, print_turn


def message_content_to_str(content: object) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def invoke_model(model: ChatOllama, messages: list[tuple[str, str]]) -> str:
    try:
        response = model.invoke(messages)
    except Exception:
        return "Model call failed safely. Check your local model configuration."

    return message_content_to_str(response.content)


def main() -> None:
    print_section("04 Model Provider Setup")

    config = load_config()
    model = get_chat_model(config)

    user_message = "Which model provider is this project currently using?"

    provider_summary = (
        f"Current provider: {config.model_provider}\n"
        f"Ollama model: {config.ollama_model}\n"
        f"Ollama base URL: {config.ollama_base_url}"
    )

    messages = [
        (
            "system",
            "You are a concise learning assistant. "
            "Answer only from the provider summary supplied by the program. "
            "Reply in one short sentence.",
        ),
        (
            "human",
            (
                f"Provider summary:\n{provider_summary}\n\n"
                f"User question: {user_message}"
            ),
        ),
    ]

    assistant_message = invoke_model(model, messages)

    print_section("Provider check")
    print_turn("provider summary", provider_summary)
    print_turn("user", user_message)
    print_turn("assistant", assistant_message)

    print_section("Conclusion")
    print()
    print(
        "The project now has a provider switch. "
        "Ollama remains the default local provider, while OpenRouter can be enabled later through environment variables."
    )


if __name__ == "__main__":
    main()