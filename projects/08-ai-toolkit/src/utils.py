"""Utility functions for the tool-calling framework."""
import time
import functools
import jsonschema
from typing import Any, Callable, TypeVar

from config import TOOL_CONFIG

T = TypeVar('T')


class ValidationError(Exception):
    """Raised when tool validation fails."""
    pass


def retry_with_backoff(max_attempts: int = None, initial_delay: float = None):
    """Decorator for retrying functions with exponential backoff."""
    max_attempts = max_attempts or TOOL_CONFIG["retry_attempts"]
    initial_delay = initial_delay or TOOL_CONFIG["retry_delay"]

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = initial_delay * (2 ** attempt)
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def validate_tool_arguments(tool_name: str, arguments: dict, schema: dict) -> bool:
    """Validate tool arguments against JSON schema.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments to validate
        schema: JSON schema definition
        
    Raises:
        ValidationError: If validation fails
    """
    if not arguments:
        arguments = {}

    try:
        jsonschema.validate(instance=arguments, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        raise ValidationError(f"Validation failed for {tool_name}: {e.message}")


def parse_arguments(arguments: dict) -> dict:
    """Parse arguments, converting strings to ints where appropriate."""
    if not arguments:
        return {}
    return {
        k: int(v) if isinstance(v, str) and v.isdigit() else v
        for k, v in arguments.items() if k
    }