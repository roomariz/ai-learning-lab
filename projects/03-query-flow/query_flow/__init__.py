"""QueryFlow - Explainable Query Orchestration + Retrieval Engine.

A lightweight retrieval framework combining dense (semantic), sparse (BM25),
and query-aware selection for improved search relevance with full explainability.

Position: "Explainable Retrieval + Query Orchestration Engine"

Quick Start:
    from query_flow import Pipeline, pipelines, QueryAnalyzer
    
    # Use ready-made pipeline
    flow = pipelines.rag(k=5)
    result = flow.run("your query", debug=True)
    
    # Or build custom
    flow = Pipeline().add_node("retrieval", "statistical").add_node("llm", "llm")
"""

from .pipeline import Pipeline, Node, PipelineResult

from .retrieval import (
    StatisticalRetriever,
    RetrievalResult,
)

from .analyzer import (
    QueryAnalyzer,
    QueryType,
    QueryAnalysis,
)

from .config import (
    PipelineBuilder,
    create_statistical_pipeline,
    create_hybrid_pipeline,
    create_smart_pipeline,
    get_config,
    create_from_config,
)
from .health import check

from . import pipelines
from . import data
from . import examples
from .data import Dataset

from .query import QueryType as QueryTypeEnum
from .selection import rank_results, filter_by_threshold

__version__ = "0.2.0"

_QUERY_FLOW_EXPORTS = {
    "retrieve_dense",
    "retrieve_bm25",
    "retrieve_smart",
    "experimental_selection",
    "detect_query_type",
    "compute_all_metrics",
    "set_documents",
    "set_embedding_model",
    "retrieve",
}

_EVALUATION_EXPORTS = {
    "Evaluator",
    "EvaluationResult",
    "evaluate_pipeline",
    "evaluate_all_methods",
}

_LAZY_MODULE_EXPORTS = {
    "benchmark": ".benchmark",
}

__all__ = [
    # Core retrieval
    "retrieve",
    "retrieve_dense",
    "retrieve_bm25",
    "retrieve_smart",
    "experimental_selection",
    "detect_query_type",
    "compute_all_metrics",
    "set_documents",
    "set_embedding_model",
    
    # Pipeline SDK
    "Pipeline",
    "Node",
    "PipelineResult",
    
    # Retrieval module
    "StatisticalRetriever",
    "RetrievalResult",
    
    # Query analysis
    "QueryAnalyzer",
    "QueryType",
    "QueryAnalysis",
    "QueryTypeEnum",
    
    # Evaluation
    "Evaluator",
    "EvaluationResult",
    "evaluate_pipeline",
    "evaluate_all_methods",
    
    # Config-based pipelines
    "PipelineBuilder",
    "create_statistical_pipeline",
    "create_hybrid_pipeline",
    "create_smart_pipeline",
    "get_config",
    "create_from_config",
    "check",
    
    # Ready-to-use pipelines
    "pipelines",
    
    # Data loading
    "data",
    "Dataset",
    
    # Examples
    "examples",
    
    # Benchmark
    "benchmark",
    
    # Utilities
    "rank_results",
    "filter_by_threshold",
]


def __getattr__(name):
    if name in _QUERY_FLOW_EXPORTS:
        from . import query_flow as _query_flow

        if name == "retrieve":
            return _query_flow.retrieve_smart
        return getattr(_query_flow, name)

    if name in _EVALUATION_EXPORTS:
        from .evaluation import (
            Evaluator,
            EvaluationResult,
            evaluate_pipeline,
            evaluate_all_methods,
        )

        exports = {
            "Evaluator": Evaluator,
            "EvaluationResult": EvaluationResult,
            "evaluate_pipeline": evaluate_pipeline,
            "evaluate_all_methods": evaluate_all_methods,
        }
        return exports[name]

    if name in _LAZY_MODULE_EXPORTS:
        import importlib

        module = importlib.import_module(_LAZY_MODULE_EXPORTS[name], __name__)
        globals()[name] = module
        return module

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
