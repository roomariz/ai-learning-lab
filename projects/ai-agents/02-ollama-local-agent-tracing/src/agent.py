from typing import Any

from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE
from tools import compute_arithmetic, get_energy_metric


SYSTEM_PROMPT = (
    "You are a precise tool-using assistant. "
    "You must answer only from the provided tools. "
    "For energy comparison questions, first identify the required metrics. "
    "If you do not yet have the numeric metric values, call only get_energy_metric. "
    "Do not call compute_arithmetic in the same step as get_energy_metric. "
    "After the get_energy_metric observations are returned, call compute_arithmetic "
    "with operation='divide' and the actual numeric values returned by the tools. "
    "Never pass placeholders, metric names, strings, or invented values into compute_arithmetic. "
    "Never guess, estimate, or invent metric values. "
    "If a required metric is unavailable, say that the metric is unavailable."
)


def create_energy_agent() -> Any:
    llm = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=OLLAMA_TEMPERATURE,
    )

    return create_agent(
        model=llm,
        tools=[get_energy_metric, compute_arithmetic],
        system_prompt=SYSTEM_PROMPT,
    )