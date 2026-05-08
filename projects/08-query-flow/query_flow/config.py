"""Config-based pipeline support for QueryFlow."""

import json
import logging
from pathlib import Path
from typing import Union, Optional
from .pipeline import Pipeline

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

logger = logging.getLogger(__name__)


class PipelineBuilder:
    """Build pipelines from configuration."""

    NODE_TYPE_MAP = {
        "retrieval": "retrieval",
        "statistical": "statistical",
        "bm25": "bm25",
        "dense": "dense",
        "llm": "llm",
        "filter": "filter",
        "rank": "rank",
    }

    @classmethod
    def from_dict(cls, config: dict) -> Pipeline:
        """Build pipeline from dictionary configuration."""
        pipeline = Pipeline(name=config.get("name", "default"))

        steps = config.get("steps", [])
        connections = config.get("connections", [])

        for step in steps:
            step_name = step.get("step")
            step_type = step.get("type")
            params = step.get("params", {})

            node_type = cls.NODE_TYPE_MAP.get(step_type, step_type)

            pipeline.add_node(step_name, node_type, **params)

        for conn in connections:
            from_node = conn.get("from")
            to_node = conn.get("to")
            if from_node and to_node:
                pipeline.connect(from_node, to_node)

        logger.info(f"Built pipeline '{pipeline.name}' with {len(steps)} steps")
        return pipeline

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> Pipeline:
        """Build pipeline from YAML file."""
        if yaml is None:
            raise ImportError(
                "PyYAML is required for YAML config support. "
                "Install with: pip install 'query-flow[yaml]'"
            )
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return cls.from_dict(config)

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> Pipeline:
        """Build pipeline from JSON file."""
        with open(path, "r") as f:
            config = json.load(f)
        return cls.from_dict(config)

    @classmethod
    def from_string(cls, config_str: str, format: str = "yaml") -> Pipeline:
        """Build pipeline from string configuration."""
        if format == "yaml":
            if yaml is None:
                raise ImportError(
                    "PyYAML is required for YAML config support. "
                    "Install with: pip install 'query-flow[yaml]'"
                )
            config = yaml.safe_load(config_str)
        elif format == "json":
            config = json.loads(config_str)
        else:
            raise ValueError(f"Unknown format: {format}")
        return cls.from_dict(config)


def create_statistical_pipeline(k: int = 5) -> Pipeline:
    """Create a default statistical retrieval pipeline."""
    return (
        Pipeline("statistical")
        .add_node("retrieval", "statistical", k=k)
    )


def create_hybrid_pipeline(k: int = 5) -> Pipeline:
    """Create a hybrid dense + BM25 pipeline."""
    return (
        Pipeline("hybrid")
        .add_node("dense", "dense", k=k)
        .add_node("bm25", "bm25", k=k)
    )


def create_smart_pipeline(k: int = 5) -> Pipeline:
    """Create a smart retrieval pipeline with query routing."""
    return (
        Pipeline("smart")
        .add_node("retrieval", "retrieval", k=k)
    )


DEFAULT_CONFIGS = {
    "statistical": {
        "name": "statistical",
        "steps": [
            {"step": "retrieval", "type": "statistical", "params": {"k": 5}}
        ],
        "connections": []
    },
    "hybrid": {
        "name": "hybrid",
        "steps": [
            {"step": "dense", "type": "dense", "params": {"k": 5}},
            {"step": "bm25", "type": "bm25", "params": {"k": 5}}
        ],
        "connections": []
    },
    "smart": {
        "name": "smart",
        "steps": [
            {"step": "retrieval", "type": "retrieval", "params": {"k": 5}}
        ],
        "connections": []
    },
    "llm_rag": {
        "name": "llm_rag",
        "steps": [
            {"step": "retrieval", "type": "statistical", "params": {"k": 5}},
            {"step": "llm", "type": "llm", "params": {"model": "llama3", "temperature": 0.7}}
        ],
        "connections": [
            {"from": "retrieval", "to": "llm"}
        ]
    }
}


def get_config(name: str) -> dict:
    """Get a default pipeline configuration by name."""
    return DEFAULT_CONFIGS.get(name, DEFAULT_CONFIGS["statistical"])


def create_from_config(name: str) -> Pipeline:
    """Create a pipeline from a named default configuration."""
    config = get_config(name)
    return PipelineBuilder.from_dict(config)
