"""Structured logging for the tool-calling framework."""
import logging
import json
import sys
from datetime import datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Format logs as JSON."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name

        if hasattr(record, "function_name"):
            log_data["function_name"] = record.function_name

        if hasattr(record, "arguments"):
            log_data["arguments"] = record.arguments

        if hasattr(record, "result"):
            log_data["result"] = record.result

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str = "tool_calling", level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """Setup structured logger.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path to write logs
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def log_tool_call(tool_name: str, arguments: dict):
    """Log tool call."""
    logger.info(f"Calling tool: {tool_name}", extra={"tool_name": tool_name, "arguments": arguments})


def log_tool_result(tool_name: str, result: str):
    """Log tool result."""
    logger.info(f"Tool completed: {tool_name}", extra={"tool_name": tool_name, "result": result[:200]})


def log_tool_error(tool_name: str, error: str):
    """Log tool error."""
    logger.error(f"Tool failed: {tool_name}", extra={"tool_name": tool_name, "error": error})


def log_llm_call(prompt: str):
    """Log LLM call."""
    logger.debug(f"LLM call: {prompt[:100]}...")


def log_llm_response(response: str):
    """Log LLM response."""
    logger.debug(f"LLM response: {response[:200]}...")