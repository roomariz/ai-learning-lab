from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    model_provider: str

    ollama_model: str
    ollama_base_url: str

    openrouter_api_key: str | None
    openrouter_model: str
    openrouter_base_url: str


def load_config() -> AppConfig:
    """
    Load local development configuration.

    Prints whether .env was found and loaded.
    """
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"

    env_loaded = load_dotenv(dotenv_path=env_path)

    model_provider = getenv("MODEL_PROVIDER", "ollama").lower()

    ollama_model = getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    ollama_base_url = getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    openrouter_api_key = getenv("OPENROUTER_API_KEY")
    openrouter_model = getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_base_url = getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    print(f"[config] Project root: {project_root}")
    print(f"[config] .env path: {env_path}")
    print(f"[config] .env loaded: {env_loaded}")
    print(f"[config] MODEL_PROVIDER: {model_provider}")

    if model_provider == "ollama":
        print(f"[config] OLLAMA_MODEL: {ollama_model}")
        print(f"[config] OLLAMA_BASE_URL: {ollama_base_url}")

    if model_provider == "openrouter":
        print(f"[config] OPENROUTER_MODEL: {openrouter_model}")
        print(f"[config] OPENROUTER_BASE_URL: {openrouter_base_url}")
        print(f"[config] OPENROUTER_API_KEY loaded: {bool(openrouter_api_key)}")

    return AppConfig(
        model_provider=model_provider,
        ollama_model=ollama_model,
        ollama_base_url=ollama_base_url,
        openrouter_api_key=openrouter_api_key,
        openrouter_model=openrouter_model,
        openrouter_base_url=openrouter_base_url,
    )