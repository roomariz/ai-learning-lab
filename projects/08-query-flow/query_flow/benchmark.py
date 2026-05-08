"""Lightweight benchmarking for QueryFlow retrieval methods."""

import logging
from typing import Optional

try:
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    pd = None
from .deps import require

logger = logging.getLogger(__name__)


def _require_pandas(purpose: str):
    if pd is None:
        require("pandas", purpose, "benchmark")


def run_default(dataset: list = None, k: int = 5) -> pd.DataFrame:
    """Run benchmark comparing all retrieval methods.
    
    Args:
        dataset: List of dicts with 'query' and 'ground_truth' keys
                 If None, uses a small built-in dataset
        k: Number of results to retrieve
    
    Returns:
        DataFrame with comparison of all methods
    """
    _require_pandas("benchmarking")
    from .query_flow import (
        retrieve_dense, retrieve_bm25, retrieve_smart, 
        experimental_selection, set_documents, SAMPLE_DOCUMENTS
    )

    if dataset is None:
        dataset = [
            {"query": "famous scientists", "ground_truth": ["doc_001", "doc_002"]},
            {"query": "mathematicians", "ground_truth": ["doc_003", "doc_041"]},
            {"query": "physicists who developed theory", "ground_truth": ["doc_001", "doc_012"]},
        ]

    set_documents(SAMPLE_DOCUMENTS)

    methods = {
        "dense": lambda q: [x[0] for x in retrieve_dense(q, k)],
        "bm25": lambda q: [x[0] for x in retrieve_bm25(q, k)],
        "hybrid": lambda q: [r["doc_id"] for r in experimental_selection(q, k)],
        "smart": lambda q: retrieve_smart(q, k),
        "statistical": lambda q: [r["doc_id"] for r in experimental_selection(q, k)]
    }

    results = []

    for item in dataset:
        query = item["query"]
        gt = item["ground_truth"]

        for method_name, method_fn in methods.items():
            retrieved = method_fn(query)
            score = _compute_precision(retrieved, gt, k)
            results.append({
                "query": query,
                "method": method_name,
                "precision_at_k": score,
                "ground_truth": gt
            })

    df = pd.DataFrame(results)
    summary = df.groupby("method")["precision_at_k"].mean().reset_index()
    summary.columns = ["method", "avg_precision"]

    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"\nDataset: {len(dataset)} queries")
    print(f"K: {k}")
    print("\n--- Average Precision@k ---")
    print(summary.to_string(index=False))
    print("="*60 + "\n")

    return summary


def _compute_precision(retrieved: list, ground_truth: list, k: int) -> float:
    """Compute precision@k."""
    retrieved = set(retrieved[:k])
    gt = set(ground_truth)
    if k == 0:
        return 0.0
    return len(retrieved & gt) / k


def compare_methods(methods: dict, dataset: list, k: int = 5) -> pd.DataFrame:
    """Compare custom methods on a dataset.
    
    Args:
        methods: Dict of {name: function} where function takes query and returns doc_ids
        dataset: List of {query, ground_truth}
        k: Number of results
    
    Returns:
        DataFrame with per-query and aggregate results
    """
    _require_pandas("benchmarking")
    results = []

    for item in dataset:
        query = item["query"]
        gt = item["ground_truth"]

        for method_name, method_fn in methods.items():
            retrieved = method_fn(query)
            precision = _compute_precision(retrieved, gt, k)
            results.append({
                "query": query,
                "method": method_name,
                "precision_at_k": precision
            })

    df = pd.DataFrame(results)
    summary = df.groupby("method")["precision_at_k"].mean().reset_index()
    summary.columns = ["method", "avg_precision"]

    return summary


__all__ = ["run_default", "compare_methods"]
