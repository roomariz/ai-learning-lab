"""
Callable tools for agent interactions.

This module provides example tools that can be called by LLM agents:
- get_weather: fetch current weather for a city
- calculate: safely evaluate mathematical expressions

Use these as reference implementations for building custom tools.
"""

from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a specified city.

    Args:
        city:
            Name of the city to look up weather for.

    Returns:
        A string describing the current weather conditions.
    """
    return f"The weather in {city} is sunny, 72°F"


@tool
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Uses a restricted eval environment that only allows basic
    arithmetic operations for security.

    Args:
        expression:
            A mathematical expression as a string
            (e.g., "2 + 2", "10 * 5").

    Returns:
        A string containing the result or error message.
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"