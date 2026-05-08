"""Configuration for the tool-calling framework."""

import os
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent

LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "llama3.1:latest"),
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "temperature": 0.7,
    "max_tokens": 2048,
}

TOOL_CONFIG = {
    "max_iterations": 5,
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
}

DEBUG = False