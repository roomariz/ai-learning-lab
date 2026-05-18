from langchain_ollama import ChatOllama

from src.common.config import load_config


def get_chat_model() -> ChatOllama:
    """
    Return the local Ollama chat model used by all labs.

    temperature=0 keeps outputs more predictable for learning examples.
    """
    config = load_config()

    return ChatOllama(
        model=config.ollama_model,
        base_url=config.ollama_base_url,
        temperature=0,
    )