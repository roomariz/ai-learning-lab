import asyncio
import json
import os
import re
import urllib.request
from urllib.error import URLError

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

DEFAULT_OLLAMA_MODELS = (
    "qwen2.5:7b",
    "qwen2.5:3b",
    "llama3.1:8b",
    "llama3.2:3b",
    "phi3:mini",
)


async def list_ollama_models(base_url: str) -> list[str]:
    def _load_models() -> list[str]:
        url = f"{base_url.rstrip('/')}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                payload = json.load(response)
        except URLError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {base_url}. Start the Ollama server "
                "or set OLLAMA_HOST to the correct URL."
            ) from exc

        return [
            model["name"]
            for model in payload.get("models", [])
            if isinstance(model, dict) and model.get("name")
        ]

    return await asyncio.to_thread(_load_models)


async def resolve_ollama_model() -> str:
    configured_model = os.getenv("OLLAMA_MODEL")
    if configured_model:
        return configured_model

    base_url = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    available_models = await list_ollama_models(base_url)

    for candidate in DEFAULT_OLLAMA_MODELS:
        if candidate in available_models:
            return candidate

    if available_models:
        return available_models[0]

    raise RuntimeError(
        "No Ollama models were found. Set OLLAMA_MODEL to an installed model "
        "name, or pull one with `ollama pull <model>`."
    )


def parse_tool_request(content: str) -> dict[str, object] | None:
    text = content.strip()
    if not text:
        return None

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    if not isinstance(payload, dict):
        return None

    if "name" not in payload or "arguments" not in payload:
        return None

    if not isinstance(payload["name"], str) or not isinstance(payload["arguments"], dict):
        return None

    return payload


def coerce_arguments(arguments: dict[str, object], last_result: int | None) -> dict[str, int]:
    coerced: dict[str, int] = {}

    for key, value in arguments.items():
        if isinstance(value, int):
            coerced[key] = value
            continue

        if isinstance(value, str):
            text = value.strip()
            if text.lstrip("-").isdigit():
                coerced[key] = int(text)
                continue

            if last_result is not None:
                coerced[key] = last_result
                continue

        raise RuntimeError(f"Could not coerce argument {key!r} from {value!r}")

    return coerced


async def main():
    client = MultiServerMCPClient({
        "math": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        }
    })

    tools = await client.get_tools()
    tools_by_name = {tool.name: tool for tool in tools}
    ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    ollama_model = await resolve_ollama_model()
    llm = ChatOllama(
        model=ollama_model,
        base_url=ollama_host,
        temperature=0,
        disable_streaming="tool_calling",
    )

    messages = [
        SystemMessage(
            content="""
You are a math assistant.
When you need a tool, reply with exactly one JSON object:
{"name":"tool_name","arguments":{"a":1,"b":2}}
Use only the provided tools.
Use one tool call at a time.
After a tool result, either request the next tool or provide the final answer.
Do not add commentary when asking for a tool.
"""
        ),
        HumanMessage(content="What is 3 multiplied by 7, then add 5?"),
    ]

    last_result: int | None = None
    final_answer: str | None = None

    for _ in range(6):
        response = await llm.ainvoke(messages)
        tool_request = parse_tool_request(response.content)
        if tool_request is None:
            final_answer = response.content.strip()
            break

        tool_name = tool_request["name"]
        raw_arguments = tool_request["arguments"]
        tool = tools_by_name.get(tool_name)
        if tool is None:
            raise RuntimeError(f"Model requested unknown tool: {tool_name}")

        call_arguments = coerce_arguments(raw_arguments, last_result)
        tool_result = await tool.ainvoke(call_arguments)

        if isinstance(tool_result, int):
            last_result = tool_result
        elif isinstance(tool_result, str) and tool_result.strip().lstrip("-").isdigit():
            last_result = int(tool_result.strip())

        messages.append(response)
        messages.append(
            HumanMessage(
                content=(
                    f"Tool {tool_name} returned {tool_result}. "
                    "Continue with the next step or give the final answer."
                )
            )
        )

    if final_answer is not None:
        print(final_answer)

if __name__ == "__main__":
    asyncio.run(main())
