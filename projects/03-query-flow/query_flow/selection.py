"""Selection and ranking utilities."""

from typing import List

from .core import RetrievalResult
from .retrieval import StatisticalRetriever


def rank_results(results: List[RetrievalResult], key: str = "final_score", reverse: bool = True) -> List[RetrievalResult]:
    return sorted(results, key=lambda r: r.get(key, 0.0), reverse=reverse)


def filter_by_threshold(results: List[RetrievalResult], threshold: float, key: str = "final_score") -> List[RetrievalResult]:
    return [r for r in results if r.get(key, 0.0) >= threshold]


__all__ = [
    "rank_results",
    "filter_by_threshold",
    "StatisticalRetriever",
]
