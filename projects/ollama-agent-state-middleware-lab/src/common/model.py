from typing import Any

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.common.config import AppConfig, load_config


def get_chat_model(config: AppConfig | None = None) -> Any:
    """
    Return the configured chat model.

    Default provider is Ollama for local-first learning.
    OpenRouter is optional and uses an OpenAI-compatible endpoint.
    """
    config = config or load_config()

    if config.model_provider == "ollama":
        return ChatOllama(
            model=config.ollama_model,
            base_url=config.ollama_base_url,
            temperature=0,
        )

    if config.model_provider == "openrouter":
        if not config.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when MODEL_PROVIDER=openrouter."
            )

        return ChatOpenAI(
            model=config.openrouter_model,
            api_key=config.openrouter_api_key,
            base_url=config.openrouter_base_url,
            temperature=0,
        )

    raise ValueError(
        f"Unsupported MODEL_PROVIDER={config.model_provider}. "
        "Use 'ollama' or 'openrouter'."
    )