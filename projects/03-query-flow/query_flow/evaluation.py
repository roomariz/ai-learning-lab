"""Evaluation toolkit for QueryFlow."""

import logging
from typing import Optional, Callable
from dataclasses import dataclass

try:
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    pd = None
from .deps import require

logger = logging.getLogger(__name__)


def _require_pandas(purpose: str):
    if pd is None:
        require("pandas", purpose, "benchmark")


@dataclass
class EvaluationResult:
    """Evaluation result for a retrieval method."""
    method: str
    precision_at_k: float
    recall_at_k: float
    f1_at_k: float
    mrr: float
    ndcg_at_k: float

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "precision@k": round(self.precision_at_k, 4),
            "recall@k": round(self.recall_at_k, 4),
            "f1@k": round(self.f1_at_k, 4),
            "mrr": round(self.mrr, 4),
            "ndcg@k": round(self.ndcg_at_k, 4)
        }


class Evaluator:
    """Evaluate retrieval methods on datasets."""

    def __init__(self, k: int = 5):
        self.k = k

    def compute_metrics(self, retrieved: list, ground_truth: list) -> dict:
        """Compute all metrics for a single query."""
        from .query_flow import compute_all_metrics
        return compute_all_metrics(retrieved, ground_truth, self.k)

    def evaluate_method(
        self,
        retrieval_fn: Callable[[str], list],
        dataset: list
    ) -> EvaluationResult:
        """Evaluate a single retrieval method on a dataset."""
        from .query_flow import (
            precision_at_k, recall_at_k, f1_score_at_k,
            mrr, ndcg_at_k
        )

        precisions, recalls, f1s, mrrs, ndcgs = [], [], [], [], []

        for item in dataset:
            query = item.get("query")
            gt = item.get("ground_truth", [])

            if not query or not gt:
                continue

            retrieved = retrieval_fn(query)

            precisions.append(precision_at_k(retrieved, gt, self.k))
            recalls.append(recall_at_k(retrieved, gt, self.k))
            f1s.append(f1_score_at_k(retrieved, gt, self.k))
            mrrs.append(mrr(retrieved, gt))
            ndcgs.append(ndcg_at_k(retrieved, gt, self.k))

        return EvaluationResult(
            method=retrieval_fn.__name__ if hasattr(retrieval_fn, "__name__") else "unknown",
            precision_at_k=sum(precisions) / len(precisions) if precisions else 0,
            recall_at_k=sum(recalls) / len(recalls) if recalls else 0,
            f1_at_k=sum(f1s) / len(f1s) if f1s else 0,
            mrr=sum(mrrs) / len(mrrs) if mrrs else 0,
            ndcg_at_k=sum(ndcgs) / len(ndcgs) if ndcgs else 0
        )

    def compare_methods(
        self,
        retrieval_fns: dict[str, Callable],
        dataset: list
    ) -> pd.DataFrame:
        """Compare multiple retrieval methods."""
        _require_pandas("evaluation comparison")
        results = []

        for name, fn in retrieval_fns.items():
            result = self.evaluate_method(fn, dataset)
            results.append(result.to_dict())

        df = pd.DataFrame(results)
        logger.info(f"Comparison complete for {len(retrieval_fns)} methods")
        return df


def evaluate_pipeline(
    pipeline,
    dataset: list,
    k: int = 5
) -> dict:
    """Evaluate a pipeline on a dataset."""
    evaluator = Evaluator(k=k)

    def retrieval_fn(query):
        result = pipeline.run(query)
        if hasattr(result, "results"):
            result = result.results
        if isinstance(result, list):
            if result and isinstance(result[0], dict):
                return [r.get("doc_id", r.get("id", "")) for r in result]
            return result
        return []

    return evaluator.evaluate_method(retrieval_fn, dataset).to_dict()


def evaluate_all_methods(
    dataset: list,
    k: int = 5
) -> pd.DataFrame:
    """Evaluate all built-in retrieval methods."""
    _require_pandas("evaluation comparison")
    from .query_flow import (
        retrieve_dense, retrieve_bm25, retrieve_smart, experimental_selection
    )

    evaluator = Evaluator(k=k)

    methods = {
        "dense": lambda q: [x[0] for x in retrieve_dense(q, k)],
        "bm25": lambda q: [x[0] for x in retrieve_bm25(q, k)],
        "smart": lambda q: retrieve_smart(q, k),
        "statistical": lambda q: experimental_selection(q, k)
    }

    return evaluator.compare_methods(methods, dataset)
