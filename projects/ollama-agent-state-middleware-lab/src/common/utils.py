"""
General utilities.

Currently used by Lab 05 for simple JSON-based state persistence.
"""

import json
import logging
from pathlib import Path
from typing import Any


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def load_json_file(path: str | Path) -> dict[str, Any] | None:
    file_path = Path(path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def save_json_file(path: str | Path, data: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)