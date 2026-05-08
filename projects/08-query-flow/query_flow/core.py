"""Core types and utilities for QueryFlow."""

from typing import TypedDict


class RetrievalResult(TypedDict):
    doc_id: str
    final_score: float
    dense_score: float
    bm25_score: float
    rule_score: float
    metadata_score: float
    text: str