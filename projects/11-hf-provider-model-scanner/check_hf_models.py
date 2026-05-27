from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from huggingface_hub import InferenceClient, whoami
from rich.console import Console


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Re-probe a few models from the last scanner report.")
    parser.add_argument(
        "--report",
        default=str(Path(__file__).parent / "reports" / "hf_model_availability.json"),
        help="Path to hf_model_availability.json (default: ./reports/hf_model_availability.json).",
    )
    parser.add_argument("--limit", type=int, default=5, help="How many models to probe.")
    parser.add_argument("--provider", default="auto", help="Inference provider routing (default: auto).")
    parser.add_argument("--timeout", type=int, default=60, help="Per-request timeout seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()

    try:
        username = whoami()["name"]
    except Exception:
        username = "unknown"

    report_path = Path(args.report).expanduser()
    if not report_path.exists():
        console.print(f"[red]Report not found:[/red] {report_path}")
        console.print("Run `python hf_model_scanner.py --output-dir reports` first.")
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    models = [
        str(r.get("model"))
        for r in rows
        if isinstance(r, dict) and str(r.get("status", "")).startswith("CONNECTED")
    ][: max(0, args.limit)]

    if not models:
        console.print("[yellow]No CONNECTED models found in report.[/yellow]")
        return 1

    console.print(f"Logged in as: [bold green]{username}[/bold green]")
    console.print(f"Probing {len(models)} model(s) via provider routing: [cyan]{args.provider}[/cyan]\n")

    client = InferenceClient(provider=args.provider, timeout=args.timeout)
    for model_id in models:
        start = time.perf_counter()
        try:
            response = client.chat_completion(
                model=model_id,
                messages=[{"role": "user", "content": "Reply with exactly: connected"}],
                max_tokens=20,
                temperature=0,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            text = response.choices[0].message.content.strip()
            console.print(f"[green]OK[/green] {model_id} ({elapsed_ms:.0f}ms): {text!r}")
        except Exception as exc:
            console.print(f"[red]FAIL[/red] {model_id}: {str(exc).replace(chr(10), ' ')[:240]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

