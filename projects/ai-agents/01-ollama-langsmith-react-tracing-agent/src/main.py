import ast
import operator

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


load_dotenv()

ENERGY_DATA = {
    "uk_wind_generation_gwh": 82_300,
    "uk_solar_generation_gwh": 14_900,
    "spain_wind_generation_gwh": 62_100,
    "spain_solar_generation_gwh": 45_200,
}


@tool
def get_energy_metric(metric_name: str) -> str:
    """
    Retrieve a renewable-energy metric from the local dataset.

    Example keys:
    - uk_wind_generation_gwh
    - uk_solar_generation_gwh
    - spain_wind_generation_gwh
    - spain_solar_generation_gwh
    """
    normalised_key = metric_name.strip().lower().replace(" ", "_")
    metric_value = ENERGY_DATA.get(normalised_key)

    if metric_value is None:
        return f"Metric not available: {normalised_key}"

    return str(metric_value)


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)

    raise ValueError("Only simple arithmetic expressions are supported.")


@tool
def compute_arithmetic(expression: str) -> str:
    """
    Safely compute a simple arithmetic expression.

    Supported operations:
    - addition
    - subtraction
    - multiplication
    - division

    Example:
    '82300 / 14900'
    """
    try:
        parsed_expression = ast.parse(expression, mode="eval")
        answer = _safe_eval(parsed_expression)
        return str(round(answer, 2))
    except Exception as error:
        return f"Calculation failed: {error}"


llm = ChatOllama(
    model="llama3.1",
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=[get_energy_metric, compute_arithmetic],
    system_prompt=(
        "You are a tool-using assistant. Answer only from the provided tools. "
        "When the user asks about energy metrics, identify the required metric keys yourself. "
        "First call get_energy_metric for each required metric. "
        "After receiving the numeric values, call compute_arithmetic using only numbers. "
        "Never pass metric names into compute_arithmetic. "
        "Do not guess, assume, or invent any data. "
        "If a required metric is not available, say that the metric is not available."
    ),
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Compare the UK's wind generation with its solar generation. "
                    "Calculate the ratio as wind generation divided by solar generation."
                ),
            }
        ]
    }
)

print("\nFinal answer:")
print(result["messages"][-1].content)

print("\nTool calls:")
for message in result["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print(f"- {tool_call['name']}: {tool_call['args']}")

print("\nTool observations:")
for message in result["messages"]:
    if message.__class__.__name__ == "ToolMessage":
        print(f"- {message.name}: {message.content}")