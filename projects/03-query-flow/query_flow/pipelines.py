"""Ready-to-use pipelines for common use cases."""

from .pipeline import Pipeline


def statistical(k: int = 5) -> Pipeline:
    """Create a statistical retrieval pipeline.
    
    Uses hybrid dense + BM25 + rule-based scoring.
    """
    return (
        Pipeline("statistical")
        .add_node("retrieval", "statistical", k=k)
    )


def hybrid(k: int = 5) -> Pipeline:
    """Create a hybrid dense + BM25 pipeline."""
    return (
        Pipeline("hybrid")
        .add_node("dense", "dense", k=k)
        .add_node("bm25", "bm25", k=k)
        .add_node("rank", "rank", key="score", reverse=True)
    )


def smart(k: int = 5) -> Pipeline:
    """Create a smart retrieval pipeline with query routing."""
    return (
        Pipeline("smart")
        .add_node("analyze", "query_analyzer")
        .add_node("retrieval", "retrieval", k=k)
    )


def rag(k: int = 5, llm_model: str = "llama3") -> Pipeline:
    """Create a RAG pipeline with retrieval + LLM.
    
    This is the killer pipeline for most use cases.
    """
    return (
        Pipeline("rag")
        .add_node("analyze", "query_analyzer")
        .add_node("retrieval", "statistical", k=k)
        .add_node("llm", "llm", model=llm_model, temperature=0.7)
        .connect("analyze", "retrieval")
        .connect("retrieval", "llm")
    )


def explainable(k: int = 5) -> Pipeline:
    """Create an explainable retrieval pipeline with full debug output."""
    return (
        Pipeline("explainable")
        .add_node("analyze", "query_analyzer")
        .add_node("retrieval", "statistical", k=k)
    )


def legal_search(k: int = 5) -> Pipeline:
    """Create a legal search pipeline optimized for case law retrieval."""
    return (
        Pipeline("legal_search")
        .add_node("analyze", "query_analyzer")
        .add_node("retrieval", "statistical", k=k, use_dense=True, use_bm25=True, use_rules=True)
    )


__all__ = [
    "statistical",
    "hybrid",
    "smart",
    "rag",
    "explainable",
    "legal_search",
]