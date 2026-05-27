from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List connected Hugging Face models from a scanner JSON report.")
    parser.add_argument(
        "--report",
        default=str(Path(__file__).parent / "reports" / "hf_model_availability.json"),
        help="Path to hf_model_availability.json (default: ./reports/hf_model_availability.json).",
    )
    parser.add_argument("--top", type=int, default=50, help="Max rows to display.")
    parser.add_argument("--agentic-only", action="store_true", help="Only show agentic-coding candidates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()
    report_path = Path(args.report).expanduser()
    if not report_path.exists():
        console.print(f"[red]Report not found:[/red] {report_path}")
        console.print("Run `python hf_model_scanner.py --output-dir reports` first.")
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    username = payload.get("huggingface_user", "unknown")
    generated_at = payload.get("generated_at", "unknown")

    connected = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if not str(row.get("status", "")).startswith("CONNECTED"):
            continue
        if args.agentic_only and not bool(row.get("agentic_coding_candidate")):
            continue
        connected.append(row)

    connected = connected[: max(0, args.top)]

    console.print(f"Logged in as: [bold green]{username}[/bold green]")
    console.print(f"Generated at: [dim]{generated_at}[/dim]\n")

    table = Table(title="Connected models", box=box.SIMPLE_HEAVY)
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Model", style="white")
    table.add_column("Status", style="green", no_wrap=True)
    table.add_column("Access", style="blue", no_wrap=True)
    table.add_column("Tier", style="magenta", no_wrap=True)
    table.add_column("Agentic", style="green", no_wrap=True)
    table.add_column("Latency", justify="right", no_wrap=True)

    for row in connected:
        latency = row.get("latency_ms")
        latency_text = "-" if latency is None else f"{float(latency):.0f}ms"
        table.add_row(
            str(row.get("provider", "")),
            str(row.get("model", "")),
            str(row.get("status", "")),
            str(row.get("access", "")),
            str(row.get("tier", "")),
            "yes" if bool(row.get("agentic_coding_candidate")) else "no",
            latency_text,
        )

    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

