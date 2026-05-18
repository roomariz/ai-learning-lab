from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    ollama_model: str
    ollama_base_url: str


def load_config() -> AppConfig:
    """
    Load local development configuration.

    Prints whether .env was found and loaded.
    """
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"

    env_loaded = load_dotenv(dotenv_path=env_path)

    print(f"[config] Project root: {project_root}")
    print(f"[config] .env path: {env_path}")
    print(f"[config] .env loaded: {env_loaded}")

    ollama_model = getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    ollama_base_url = getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    print(f"[config] OLLAMA_MODEL: {ollama_model}")
    print(f"[config] OLLAMA_BASE_URL: {ollama_base_url}")

    return AppConfig(
        ollama_model=ollama_model,
        ollama_base_url=ollama_base_url,
    )