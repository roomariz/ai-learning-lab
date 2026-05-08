"""Async tool execution for parallel tool calls."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine

from tools_map import tools_map
from utils import parse_arguments


class AsyncToolRunner:
    """Run tools asynchronously with parallel execution support."""

    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute_tool(self, function_name: str, arguments: dict) -> str:
        """Execute a single tool synchronously."""
        if not function_name:
            raise ValueError("No function name provided")

        if function_name not in tools_map:
            raise ValueError(f"Unknown tool: {function_name}")

        args = parse_arguments(arguments)

        if args:
            return tools_map[function_name](**args)
        else:
            return tools_map[function_name]()

    async def execute_tool_async(self, function_name: str, arguments: dict) -> str:
        """Execute a single tool asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.execute_tool,
            function_name,
            arguments
        )

    async def execute_multiple(self, tool_calls: list) -> list[dict]:
        """Execute multiple tools in parallel."""
        tasks = [
            self.execute_tool_async(call["function"]["name"], call["function"]["arguments"])
            for call in tool_calls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {
                "function_name": tool_calls[i]["function"]["name"],
                "result": str(results[i]) if not isinstance(results[i], Exception) else f"Error: {results[i]}",
                "error": str(results[i]) if isinstance(results[i], Exception) else None
            }
            for i in range(len(tool_calls))
        ]


async def run_async(prompt: str, tools: list, max_iterations: int = 5):
    """Run the async tool-calling loop."""
    from ollama import chat
    from config import LLM_CONFIG

    messages = [
        {"role": "system", "content": "You have access to tools. Only use a tool when the user asks for something that requires it."},
        {"role": "user", "content": prompt}
    ]

    runner = AsyncToolRunner()

    for _ in range(max_iterations):
        response = chat(
            model=LLM_CONFIG["model"],
            messages=messages,
            tools=tools,
        )

        message = response["message"]

        if message.get("tool_calls"):
            results = await runner.execute_multiple(message["tool_calls"])

            for i, tool_call in enumerate(message["tool_calls"]):
                function_name = tool_call["function"]["name"]
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "name": function_name,
                    "content": results[i]["result"]
                })
        else:
            return message.get("content", "")

    return "Max iterations reached"