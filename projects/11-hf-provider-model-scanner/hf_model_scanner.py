from __future__ import annotations

import argparse
import csv
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests
from huggingface_hub import InferenceClient, whoami
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hf_report_template import build_html_report

DEFAULT_PROVIDERS = [
    "together",
    "groq",
    "fireworks-ai",
    "novita",
    "cerebras",
    "deepinfra",
    "hf-inference",
    "sambanova",
    "replicate",
]

DEFAULT_KEYWORDS = [
    "coder",
    "code",
    "qwen",
    "llama",
    "mistral",
    "gemma",
    "deepseek",
    "phi",
]

PURPOSES = {
    "coder": "Coding agent / code repair",
    "code": "Coding / programming",
    "qwen": "Coding and reasoning",
    "llama": "General reasoning / fallback",
    "mistral": "General assistant / fast reasoning",
    "gemma": "Lightweight general model",
    "deepseek": "Deep reasoning / code review",
    "phi": "Small fast reasoning",
}

AGENTIC_CODING_MARKERS = [
    "coder",
    "code repair",
    "qwen3-coder",
    "deepseek",
    "qwen3-32b",
    "qwen3-235b",
    "qwen3.5",
]

CHAT_PROBE = "Reply with exactly: connected"
EXPECTED_PROBE_REPLY = "connected"

console = Console()

HF_PROVIDERS_API_CANDIDATES = [
    "https://huggingface.co/api/inference-providers",
    "https://huggingface.co/api/inference_providers",
]


@dataclass(slots=True)
class ModelRow:
    provider: str
    model: str
    status: str = "NOT TESTED"
    tier: str = "Unknown"
    best_context: str = "General inference"
    access: str = "Unknown"
    agentic_coding_candidate: bool = False
    latency_ms: Optional[float] = None
    note: str = ""

    def to_export_dict(self) -> dict[str, object]:
        return {
            "Provider": self.provider,
            "Model": self.model,
            "Status": self.status,
            "Tier": self.tier,
            "Access": self.access,
            "Best context": self.best_context,
            "Agentic coding candidate": self.agentic_coding_candidate,
            "Latency ms": None if self.latency_ms is None else round(self.latency_ms, 2),
            "Note": self.note,
        }


def guess_context(model_id: str) -> str:
    lower = model_id.lower()
    for key, purpose in PURPOSES.items():
        if key in lower:
            return purpose
    return "General inference"


def classify_tier(model_id: str, status: str) -> str:
    lower = model_id.lower()

    if not status.startswith("CONNECTED"):
        return "Unavailable"

    if "coder-480b" in lower or "qwen3-coder" in lower:
        return "Premium coding"
    if "deepseek" in lower:
        return "Deep review"
    if "70b" in lower or "32b" in lower or "235b" in lower:
        return "Heavy reasoning"
    if "7b" in lower or "8b" in lower or "9b" in lower:
        return "Light fallback"
    return "General"


def is_agentic_coding_model(model_id: str, context: str, tier: str) -> bool:
    text = f"{model_id.lower()} {context.lower()} {tier.lower()}"
    return any(marker in text for marker in AGENTIC_CODING_MARKERS)


def compact_error(exc: Exception, limit: int = 220) -> str:
    return str(exc).replace("\n", " ").strip()[:limit]

def fetch_providers(timeout: int) -> list[str]:
    for url in HF_PROVIDERS_API_CANDIDATES:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
            providers: list[str] = []

            if isinstance(payload, dict):
                if "providers" in payload and isinstance(payload["providers"], list):
                    for item in payload["providers"]:
                        if isinstance(item, str):
                            providers.append(item)
                        elif isinstance(item, dict) and "id" in item:
                            providers.append(str(item["id"]))
                for value in payload.values():
                    if isinstance(value, str):
                        providers.append(value)
                    elif isinstance(value, dict) and "id" in value:
                        providers.append(str(value["id"]))

            if isinstance(payload, list):
                for item in payload:
                    if isinstance(item, str):
                        providers.append(item)
                    elif isinstance(item, dict):
                        if "id" in item:
                            providers.append(str(item["id"]))
                        elif "provider" in item:
                            providers.append(str(item["provider"]))

            cleaned = [
                p.strip()
                for p in providers
                if p and p.strip() and p.strip().lower() not in {"auto", "none", "null"}
            ]
            cleaned = sorted(dict.fromkeys(cleaned))
            if cleaned:
                return cleaned
        except Exception:
            continue

    return DEFAULT_PROVIDERS[:]


def sanitise_providers(providers: list[str]) -> list[str]:
    cleaned = [
        p.strip()
        for p in providers
        if p and p.strip() and p.strip().lower() not in {"auto", "none", "null"}
    ]
    return sorted(dict.fromkeys(cleaned))


def get_provider_models(provider: str, keywords: Iterable[str], timeout: int) -> list[str]:
    url = "https://huggingface.co/api/models"
    response = requests.get(
        url,
        params={"inference_provider": provider, "limit": 100},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()

    lowered_keywords = [keyword.lower() for keyword in keywords]
    models: list[str] = []

    for item in data:
        model_id = item.get("id")
        if not model_id:
            continue
        if any(keyword in model_id.lower() for keyword in lowered_keywords):
            models.append(model_id)

    return sorted(set(models))


def collect_models(providers: list[str], keywords: list[str], timeout: int) -> list[ModelRow]:
    rows: list[ModelRow] = []
    seen: set[tuple[str, str]] = set()

    for provider in providers:
        try:
            models = get_provider_models(provider, keywords, timeout)
        except Exception as exc:
            rows.append(
                ModelRow(
                    provider=provider,
                    model="-",
                    status="LIST FAILED",
                    tier="Unavailable",
                    best_context="-",
                    note=compact_error(exc),
                )
            )
            continue

        for model_id in models:
            key = (provider, model_id)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                ModelRow(
                    provider=provider,
                    model=model_id,
                    best_context=guess_context(model_id),
                )
            )

    return rows


def normalise_probe_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def classify_access(status: str, note: str) -> str:
    lower = note.lower()
    if status.startswith("CONNECTED"):
        return "Available"
    if "402 client error" in lower or "payment required" in lower:
        return "Payment required"
    if "429 client error" in lower or "rate limit" in lower or "too many requests" in lower:
        return "Rate limited"
    if status in {"FAILED", "LIST FAILED"}:
        return "Unavailable"
    return "Unknown"


def test_model(model_id: str, provider: str = "auto", timeout: int = 60) -> tuple[str, str, Optional[float]]:
    start = time.perf_counter()
    try:
        client = InferenceClient(provider=provider, timeout=timeout)
        response = client.chat_completion(
            model=model_id,
            messages=[{"role": "user", "content": CHAT_PROBE}],
            max_tokens=20,
            temperature=0,
        )
        text = response.choices[0].message.content.strip()
        normalised = normalise_probe_text(text)

        if normalised == EXPECTED_PROBE_REPLY:
            return "CONNECTED", text, (time.perf_counter() - start) * 1000

        # The request succeeded, but the model did not obey the exact probe.
        # This is useful for availability, but not strong enough for a clean CONNECTED mark.
        return "CONNECTED?", text, (time.perf_counter() - start) * 1000
    except Exception as exc:
        return "FAILED", compact_error(exc), None

def test_rows(rows: list[ModelRow], max_workers: int, timeout: int) -> list[ModelRow]:
    testable_rows = [row for row in rows if row.model != "-"]

    if max_workers <= 1:
        for row in testable_rows:
            apply_test_result(row, *test_model(row.model, row.provider, timeout=timeout))
        return rows

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(test_model, row.model, row.provider, timeout): row
            for row in testable_rows
        }
        for future in as_completed(future_map):
            row = future_map[future]
            try:
                status, note, latency_ms = future.result()
            except Exception as exc:
                status, note, latency_ms = "FAILED", compact_error(exc), None
            apply_test_result(row, status, note, latency_ms)

    return rows


def apply_test_result(row: ModelRow, status: str, note: str, latency_ms: Optional[float]) -> None:
    row.status = status
    row.note = note
    row.access = classify_access(status, note)
    row.tier = classify_tier(row.model, status)
    row.latency_ms = latency_ms
    row.agentic_coding_candidate = is_agentic_coding_model(
        row.model,
        row.best_context,
        row.tier,
    )


def summarise(rows: list[ModelRow]) -> dict[str, object]:
    metrics: dict[str, object] = {
        "total_entries": len(rows),
        "connected": sum(row.status.startswith("CONNECTED") for row in rows),
        "failed": sum(row.status == "FAILED" for row in rows),
        "payment_required": sum(row.access == "Payment required" for row in rows),
        "rate_limited": sum(row.access == "Rate limited" for row in rows),
        "agentic_coding_candidates": sum(row.agentic_coding_candidate for row in rows),
        "list_failed": sum(row.status == "LIST FAILED" for row in rows),
    }
    latencies = sorted(
        row.latency_ms for row in rows
        if row.status == "CONNECTED" and row.latency_ms is not None
    )
    if latencies:
        metrics["connected_latency_p50_ms"] = round(latencies[int(0.50 * (len(latencies) - 1))], 1)
        metrics["connected_latency_p95_ms"] = round(latencies[int(0.95 * (len(latencies) - 1))], 1)
    return metrics


def status_style(status: str) -> str:
    if status == "CONNECTED":
        return "bold green"
    if status == "CONNECTED?":
        return "bold yellow"
    if status in {"FAILED", "LIST FAILED"}:
        return "bold red"
    return "white"


def render_console(rows: list[ModelRow], username: str) -> None:
    console.print(Panel.fit("Hugging Face Provider Model Scanner", style="bold cyan"))
    console.print(f"Logged in as: [bold green]{username}[/bold green]\n")

    metrics = summarise(rows)
    summary = Table(title="Summary", box=box.ROUNDED)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Count", justify="right", style="bold")
    for key, value in metrics.items():
        summary.add_row(key.replace("_", " ").title(), str(value))
    console.print(summary)

    table = Table(title="Hugging Face Model Availability", box=box.SIMPLE_HEAVY)
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Model", style="white")
    table.add_column("Status")
    table.add_column("Access", style="blue")
    table.add_column("Tier", style="magenta")
    table.add_column("Agentic", style="green")
    table.add_column("Best context", style="yellow")
    table.add_column("Latency", style="white", justify="right", no_wrap=True)
    table.add_column("Note", style="dim", overflow="ellipsis")

    for row in rows:
        style = status_style(row.status)
        latency = "-" if row.latency_ms is None else f"{row.latency_ms:.0f}ms"
        table.add_row(
            row.provider,
            row.model,
            f"[{style}]{row.status}[/{style}]",
            row.access,
            row.tier,
            "yes" if row.agentic_coding_candidate else "no",
            row.best_context,
            latency,
            row.note[:80],
        )

    console.print(table)

    connected_agentic = [
        row for row in rows
        if row.status.startswith("CONNECTED") and row.agentic_coding_candidate
    ]

    console.print("\n[bold green]Connected agentic-coding candidates for Hermes:[/bold green]\n")
    if not connected_agentic:
        console.print("No connected agentic-coding candidates found.")
        return

    for row in connected_agentic:
        console.print(
            f"• [bold]{row.model}[/bold] "
            f"[cyan]({row.provider})[/cyan] "
            f"- [yellow]{row.tier}[/yellow] - {row.best_context}"
        )


def export_csv(rows: list[ModelRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].to_export_dict().keys()) if rows else [])
        writer.writeheader()
        writer.writerows(row.to_export_dict() for row in rows)


def export_json(rows: list[ModelRow], path: Path, username: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "huggingface_user": username,
        "summary": summarise(rows),
        "rows": [asdict(row) for row in rows],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_html(rows: list[ModelRow], path: Path, username: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    html = build_html_report(
        rows=[row.to_export_dict() for row in rows],
        summary=summarise(rows),
        username=username,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    path.write_text(html, encoding="utf-8")


def parse_csv_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Hugging Face inference-provider model availability.")
    parser.add_argument("--output-dir", default=".", help="Directory for CSV, JSON and HTML outputs.")
    parser.add_argument(
        "--providers",
        default=",".join(DEFAULT_PROVIDERS),
        help="Comma-separated provider list, or 'auto' to fetch from Hugging Face.",
    )
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS), help="Comma-separated model keyword filter.")
    parser.add_argument("--workers", type=int, default=4, help="Parallel model test workers. Use 1 for sequential mode.")
    parser.add_argument("--request-timeout", type=int, default=30, help="HTTP timeout for listing models.")
    parser.add_argument("--inference-timeout", type=int, default=60, help="Timeout for each chat-completion probe.")
    parser.add_argument("--skip-tests", action="store_true", help="Only list matching provider models. Do not test chat availability.")
    parser.add_argument(
        "--route-provider",
        choices=["auto", "listed"],
        default="auto",
        help="How to route chat probes: always via provider=auto, or use the listed provider per row.",
    )
    parser.add_argument(
        "--print-paths",
        choices=["relative", "absolute"],
        default="relative",
        help="How to print output paths at the end (default: relative).",
    )
    return parser.parse_args()

def display_path(path: Path, mode: str, base: Path) -> str:
    if mode == "absolute":
        return str(path)
    try:
        return os.path.relpath(str(path), str(base))
    except Exception:
        return str(path.name)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    if args.providers.strip().lower() == "auto":
        providers = fetch_providers(timeout=args.request_timeout)
    else:
        providers = parse_csv_arg(args.providers)
    providers = sanitise_providers(providers)
    if not providers:
        providers = DEFAULT_PROVIDERS[:]
    keywords = parse_csv_arg(args.keywords)

    try:
        username = whoami()["name"]
    except Exception as exc:
        username = "unknown"
        console.print(f"[yellow]Could not confirm Hugging Face login: {compact_error(exc)}[/yellow]")

    with console.status("[bold cyan]Collecting provider model lists..."):
        rows = collect_models(providers, keywords, args.request_timeout)

    console.print(f"Found [bold]{len(rows)}[/bold] provider/model entries.\n")

    if not args.skip_tests:
        with console.status("[bold cyan]Testing chat-compatible models..."):
            if args.route_provider == "listed":
                rows = test_rows(rows, max_workers=max(1, args.workers), timeout=args.inference_timeout)
            else:
                for row in rows:
                    row.provider = "auto"
                rows = test_rows(rows, max_workers=max(1, args.workers), timeout=args.inference_timeout)

    render_console(rows, username)

    csv_path = output_dir / "hf_model_availability.csv"
    json_path = output_dir / "hf_model_availability.json"
    html_path = output_dir / "hf_model_availability.html"

    export_csv(rows, csv_path)
    export_json(rows, json_path, username)
    export_html(rows, html_path, username)

    base = Path.cwd().resolve()
    csv_disp = display_path(csv_path, args.print_paths, base)
    json_disp = display_path(json_path, args.print_paths, base)
    html_disp = display_path(html_path, args.print_paths, base)
    print(f"\nCSV saved to: {csv_disp}")
    print(f"JSON saved to: {json_disp}")
    print(f"HTML dashboard saved to: {html_disp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
