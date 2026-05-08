"""Lightweight dependency health checks for QueryFlow."""

from __future__ import annotations

import importlib.util
from typing import Dict

from .deps import install_hint


def _is_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check(verbose: bool = False) -> Dict[str, bool]:
    """Print and return dependency status for core and optional features."""
    status = {
        "core_numpy": _is_available("numpy"),
        "yaml": _is_available("yaml"),
        "retrieval_faiss": _is_available("faiss"),
        "retrieval_bm25": _is_available("rank_bm25"),
        "retrieval_openai": _is_available("openai"),
        "benchmark_pandas": _is_available("pandas"),
    }

    print("QueryFlow health check")
    print(f"- Core numpy: {'OK' if status['core_numpy'] else 'MISSING'}")
    print(f"- YAML support: {'OK' if status['yaml'] else 'MISSING'}")
    print(f"- Retrieval extras: {'OK' if status['retrieval_faiss'] and status['retrieval_bm25'] and status['retrieval_openai'] else 'MISSING'}")
    print(f"- Benchmark extras: {'OK' if status['benchmark_pandas'] else 'MISSING'}")

    if not status["core_numpy"]:
        print(install_hint())
    if not status["yaml"]:
        print(install_hint("yaml"))
    if not (status["retrieval_faiss"] and status["retrieval_bm25"] and status["retrieval_openai"]):
        print(install_hint("retrieval"))
    if not status["benchmark_pandas"]:
        print(install_hint("benchmark"))

    if verbose:
        print("")
        print("Installed extras:")
        print(f"- yaml: {'yes' if status['yaml'] else 'no'}")
        print(f"- retrieval: {'yes' if status['retrieval_faiss'] and status['retrieval_bm25'] and status['retrieval_openai'] else 'no'}")
        print(f"- benchmark: {'yes' if status['benchmark_pandas'] else 'no'}")
        print("")
        print("Missing extras:")
        missing = []
        if not status["yaml"]:
            missing.append("yaml")
        if not (status["retrieval_faiss"] and status["retrieval_bm25"] and status["retrieval_openai"]):
            missing.append("retrieval")
        if not status["benchmark_pandas"]:
            missing.append("benchmark")
        if missing:
            for extra in missing:
                print(f"- {extra}")
        else:
            print("- none")
        print("")
        print("Example commands:")
        print('pip install "query-flow[retrieval]"')
        print('uv pip install "query-flow[retrieval]"')

    return status
