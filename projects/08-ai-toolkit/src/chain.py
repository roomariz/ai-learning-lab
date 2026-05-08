"""Tool chaining for multi-step workflows."""
import json
from typing import Callable, Any

from tools_map import tools_map
from utils import parse_arguments


class ToolChain:
    """Define and execute multi-step tool workflows."""

    def __init__(self):
        self.steps: list[tuple[str, Callable]] = []

    def add_step(self, tool_name: str, transform: Callable = None):
        """Add a step to the chain.
        
        Args:
            tool_name: Name of the tool to execute
            transform: Optional function to transform output to next input
        """
        if tool_name not in tools_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        def execute_step(args: dict) -> dict:
            args = parse_arguments(args)
            result = tools_map[tool_name](**args)
            return json.loads(result) if isinstance(result, str) else result

        if transform:
            def transformed_step(args: dict) -> dict:
                output = execute_step(args)
                return transform(output)
            self.steps.append((tool_name, transformed_step))
        else:
            self.steps.append((tool_name, execute_step))

        return self

    def execute(self, initial_args: dict) -> list[dict]:
        """Execute all steps in the chain."""
        results = []
        current_args = initial_args

        for tool_name, step_func in self.steps:
            result = step_func(current_args)
            results.append({
                "tool": tool_name,
                "result": result
            })
            current_args = result

        return results


def create_search_read_chain():
    """Create a chain: search docs -> read first result."""
    chain = ToolChain()
    chain.add_step("search_docs")
    chain.add_step("read_document", lambda doc: {"doc_id": doc.get("results", [{}])[0].get("title", "1")})
    return chain


def create_research_chain():
    """Create a chain: search -> read -> summarise."""
    chain = ToolChain()
    chain.add_step("search_docs")
    chain.add_step("read_document", lambda r: {"doc_id": "1"})
    chain.add_step("summarise_document")
    return chain