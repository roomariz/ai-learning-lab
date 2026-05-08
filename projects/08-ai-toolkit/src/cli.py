"""Interactive CLI for the tool-calling framework."""
import json
import sys
from textwrap import shorten
from ollama import chat
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from functions import search_docs, read_document, summarise_document, extract_keywords, answer_question, get_chuck_norris_fact
from tools_map import tools_map
import logging
from config import LLM_CONFIG, TOOL_CONFIG, DEBUG
from utils import retry_with_backoff, validate_tool_arguments, parse_arguments, ValidationError
from logger import log_tool_call, log_tool_result, log_tool_error

logging.getLogger("tool_calling").setLevel(logging.WARNING if not DEBUG else logging.DEBUG)

console = Console()

RENDERERS = {
    "search_docs": lambda r: render_search(r),
    "read_document": lambda r: render_read_document(r),
    "summarise_document": lambda r: render_summarise_document(r),
    "extract_keywords": lambda r: render_extract_keywords(r),
    "answer_question": lambda r: render_answer_question(r),
    "get_chuck_norris_fact": lambda r: render_chuck_norris(r),
}


def render_search(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" SEARCH DOCS ", style="bold cyan"))
    console.print(Panel(f"Query: [cyan]{data['query']}[/cyan]"))

    table = Table(style="cyan")
    table.add_column("Title", style="cyan bold")
    table.add_column("Summary")
    table.add_column("URL", style="green")

    for doc in data["results"]:
        table.add_row(doc["title"], doc["summary"], doc["url"])

    console.print(table)


def render_read_document(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" READ DOCUMENT ", style="bold blue"))

    console.print(Panel.fit(f"""[bold]ID:[/bold] {data['id']}
[bold]Source:[/bold] {data['source']}
[bold]Title:[/bold] {data['title']}""", style="blue"))

    console.print(Panel.fit(f"[bold]Preview:[/bold]\n{data['content']}", style="white"))


def render_summarise_document(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" SUMMARISE DOCUMENT ", style="bold magenta"))

    console.print(Panel(f"""[bold]Document:[/bold] {data['id']}
[bold]Word count:[/bold] {data['word_count']}""", style="magenta"))

    console.print(Panel(f"[bold]Summary:[/bold]\n{data['summary']}", style="cyan"))


def render_extract_keywords(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" EXTRACT KEYWORDS ", style="bold green"))
    console.print(Panel(f"Input: [dim]{shorten(data['text'], width=80, placeholder='...')}[/dim]", style="green"))

    console.print(f"[bold]Keywords ({data['count']}):[/bold]")
    for kw in data["keywords"]:
        console.print(f"  OK {kw}")


def render_answer_question(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" QUESTION ANSWERING ", style="bold yellow"))
    console.print(Panel(f"[bold]Question:[/bold]\n{data['question']}", style="yellow"))
    console.print(Panel(f"[bold]Confidence:[/bold] [yellow]{int(data['confidence']*100)}%[/yellow]", style="yellow"))
    console.print(Panel(f"[bold]Answer:[/bold]\n{data['answer']}", style="cyan"))


def render_chuck_norris(result):
    data = json.loads(result)
    console.print()
    console.print(Panel.fit(" CHUCK NORRIS FACT ", style="bold red"))
    console.print(Panel(f"[bold]Fact:[/bold]\n{data['fact']}", style="cyan"))
    console.print(f"OK ID: {data['id']}")
    console.print(f"OK [link]{data['url']}[/link]")


tools = [
    {"type": "function", "function": {"name": "search_docs", "description": "Search documentation for a topic", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "read_document", "description": "Read a document by its ID", "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}}, "required": ["doc_id"]}}},
    {"type": "function", "function": {"name": "summarise_document", "description": "Summarise the content of a document", "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}}, "required": ["doc_id"]}}},
    {"type": "function", "function": {"name": "extract_keywords", "description": "Extract keywords from text", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "answer_question", "description": "Answer a question based on the provided context", "parameters": {"type": "object", "properties": {"question": {"type": "string"}, "context": {"type": "string"}}, "required": ["question", "context"]}}},
    {"type": "function", "function": {"name": "get_chuck_norris_fact", "description": "Get a random Chuck Norris fact from an external API", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
]


@retry_with_backoff()
def execute_tool(function_name, arguments):
    if not function_name:
        raise ValueError("No function name provided")

    if function_name not in tools_map:
        raise ValueError(f"Unknown tool: {function_name}")

    tool_schema = next((t["function"] for t in tools if t["function"]["name"] == function_name), None)
    if tool_schema:
        params_schema = tool_schema.get("parameters", {})
        validate_tool_arguments(function_name, arguments or {}, params_schema)

    arguments = arguments or {}
    arguments = parse_arguments(arguments)

    if arguments:
        return tools_map[function_name](**arguments)
    else:
        return tools_map[function_name]()


def process_prompt(prompt: str):
    messages = [
        {"role": "system", "content": "You have access to tools. Only use a tool when the user asks for something that requires it. For general conversation, simple questions, or greetings, respond directly without using any tools."},
        {"role": "user", "content": prompt}
    ]
    max_iterations = TOOL_CONFIG["max_iterations"]
    show_assistant_response = False

    for _ in range(max_iterations):
        response = chat(model=LLM_CONFIG["model"], messages=messages, tools=tools)
        message = response["message"]

        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                func_data = tool_call.get("function", {})
                function_name = func_data.get("name")
                arguments = func_data.get("arguments", {})

                if not function_name:
                    console.print("[red]X Error: No function name in tool call[/red]")
                    continue

                console.print(f"\n... Running {function_name}...")

                try:
                    log_tool_call(function_name, arguments)
                    result = execute_tool(function_name, arguments)
                    log_tool_result(function_name, result)
                    console.print(f"OK {function_name} completed")

                    renderer = RENDERERS.get(function_name)
                    if renderer:
                        renderer(result)

                    if DEBUG:
                        console.print(Panel("[yellow]DEBUG: Tool Result (JSON)[/yellow]", style="yellow"))
                        console.print(json.loads(result))

                except Exception as e:
                    log_tool_error(function_name, str(e))
                    console.print(f"X Error: {str(e)}")
                    result = f"Tool failed: {str(e)}"

                if function_name in ["answer_question"]:
                    show_assistant_response = True

                messages.append(message)
                messages.append({"role": "tool", "name": function_name, "content": str(result)})
        elif message.get("content"):
            if show_assistant_response:
                console.print()
                console.print(Panel(f"[bold]Assistant:[/bold]\n{message['content']}", style="cyan"))
            else:
                console.print()
                console.print(message["content"])
        else:
            console.print("[yellow]No response from model[/yellow]")
        break


def main():
    console.print(Panel.fit("[bold cyan]Tool-Calling CLI[/bold cyan]", style="cyan"))
    console.print("[dim]Enter a prompt and press Enter to run. Type [bold]q[/bold] or [bold]quit[/bold] to exit.[/dim]\n")

    while True:
        try:
            if sys.platform == "win32":
                prompt = input("> ").strip()
            else:
                prompt = console.input("[bold]>[/bold] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[cyan]Goodbye![/cyan]")
            break

        if not prompt or prompt.lower() in ("q", "quit", "exit"):
            console.print("\n[cyan]Goodbye![/cyan]")
            break

        print(f"\n{'='*60}")
        console.print(f"[bold cyan]>>> {prompt}[/bold cyan]")
        print(f"{'='*60}\n")

        try:
            process_prompt(prompt)
            console.print()
            console.print("[dim]--- Done. Enter next prompt or type q/quit to exit ---[/dim]")
        except Exception as e:
            console.print(f"[red]X Error: {str(e)}[/red]")


if __name__ == "__main__":
    main()