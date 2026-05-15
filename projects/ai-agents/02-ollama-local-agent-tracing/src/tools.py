from typing import Any

from langchain_core.tools import tool


ENERGY_DATA = {
    "uk_wind_generation": 8765,
    "uk_solar_generation": 4521,
}


@tool
def get_energy_metric(metric_name: str) -> dict[str, Any]:
    """Retrieve a specific energy metric value.

    Args:
        metric_name: The name of the energy metric to retrieve.
            Supported: "uk_wind_generation", "uk_solar_generation"

    Returns:
        A dictionary with the metric name, value and unit.
    """
    normalised_metric_name = metric_name.strip().lower()

    if normalised_metric_name not in ENERGY_DATA:
        return {
            "error": (
                f"Metric '{normalised_metric_name}' not found. "
                f"Available metrics: {list(ENERGY_DATA.keys())}"
            )
        }

    return {
        "metric_name": normalised_metric_name,
        "value": ENERGY_DATA[normalised_metric_name],
        "unit": "MW",
    }


@tool
def compute_arithmetic(operation: str, a: float, b: float) -> dict[str, Any]:
    """Perform arithmetic operations on two actual numeric values.

    Use this tool only after the required numeric values have already been
    retrieved from get_energy_metric.

    Args:
        operation: Supported operations are "divide", "multiply", "add", "subtract".
        a: The first numeric value. Do not pass metric names or placeholders.
        b: The second numeric value. Do not pass metric names or placeholders.

    Returns:
        A dictionary with the operation, inputs and result.
    """
    
    normalised_operation = operation.strip().lower()

    if normalised_operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero."}
        result = a / b
    elif normalised_operation == "multiply":
        result = a * b
    elif normalised_operation == "add":
        result = a + b
    elif normalised_operation == "subtract":
        result = a - b
    else:
        return {
            "error": (
                f"Unknown operation: {normalised_operation}. "
                "Supported operations: divide, multiply, add, subtract."
            )
        }

    return {
        "operation": normalised_operation,
        "a": a,
        "b": b,
        "result": round(result, 4),
    }