"""Pipeline SDK for QueryFlow - Node and edge-based workflow orchestration."""

import logging
from typing import Any, Callable, Optional
from dataclasses import dataclass, field, asdict
from .deps import require

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    """A single step in the pipeline."""
    name: str
    node_type: str
    params: dict = field(default_factory=dict)


@dataclass
class TraceEntry:
    """A trace entry for pipeline execution."""
    step: str
    node_type: str
    input_data: Any
    output_data: Any
    metadata: dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Structured output from pipeline execution."""
    query: str
    results: list
    trace: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    debug_info: dict = field(default_factory=dict)
    debug: bool = False
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": self.results,
            "trace": self.trace,
            "metadata": self.metadata,
            "debug_info": self.debug_info,
            "debug": self.debug,
            "message": self.message
        }

    def is_debug(self) -> bool:
        """Return True when the result was produced in debug mode."""
        return self.debug


class Node:
    """Base class for pipeline nodes.
    
    All custom nodes should inherit from this and implement:
    - run(): Process input and return output
    - explain(): Return explanation of processing
    """

    def __init__(self, name: str, **params):
        self.name = name
        self.params = params
        self._last_input = None
        self._last_output = None

    def run(self, input_data: Any) -> Any:
        """Process input and return output.
        
        This is the main entry point for node execution.
        Override this in subclasses.
        """
        raise NotImplementedError

    def explain(self) -> dict:
        """Return explanation of the node's processing.
        
        Returns dict with:
        - node_name: str
        - processing_summary: str
        - scores: dict (if applicable)
        - metadata: dict
        """
        return {
            "node_name": self.name,
            "processing_summary": f"Processed input with {self.__class__.__name__}",
            "metadata": self.params
        }

    def process(self, input_data: Any) -> Any:
        """Legacy method - now calls run()."""
        return self.run(input_data)


class RetrievalNode(Node):
    """Node for retrieval operations."""

    def run(self, input_data: Any) -> Any:
        from .query_flow import retrieve_smart
        query = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = query
        result = retrieve_smart(query, k=self.params.get("k", 5))
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"Retrieved top {self.params.get('k', 5)} documents",
            "scores": {"retrieved": len(self._last_output) if self._last_output else 0},
            "metadata": self.params
        }


class BM25Node(Node):
    """Node for BM25 retrieval."""

    def run(self, input_data: Any) -> Any:
        from .query_flow import retrieve_bm25
        query = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = query
        result = retrieve_bm25(query, k=self.params.get("k", 5))
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"BM25 retrieved {len(self._last_output) if self._last_output else 0} docs",
            "metadata": self.params
        }


class DenseNode(Node):
    """Node for dense retrieval."""

    def run(self, input_data: Any) -> Any:
        from .query_flow import retrieve_dense
        query = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = query
        result = retrieve_dense(query, k=self.params.get("k", 5))
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"Dense retrieved {len(self._last_output) if self._last_output else 0} docs",
            "metadata": self.params
        }


class StatisticalNode(Node):
    """Node for statistical retrieval."""

    def __init__(self, name: str, **params):
        super().__init__(name, **params)
        self._retriever = None
        self._k = params.get("k", 5)

    def run(self, input_data: Any) -> Any:
        from .retrieval import StatisticalRetriever
        query = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = query
        
        if self._retriever is None:
            retriever_params = {k: v for k, v in self.params.items() if k != "k"}
            self._retriever = StatisticalRetriever(**retriever_params)
        
        result = self._retriever.retrieve(query, k=self._k)
        self._last_output = result
        return result

    def explain(self) -> dict:
        if self._last_output:
            scores = {
                "dense": self._last_output[0].dense_score if self._last_output else 0,
                "bm25": self._last_output[0].bm25_score if self._last_output else 0,
                "rule": self._last_output[0].rule_score if self._last_output else 0,
            }
        else:
            scores = {}
        
        return {
            "node_name": self.name,
            "processing_summary": f"Statistical retrieval returned {len(self._last_output) if self._last_output else 0} results",
            "scores": scores,
            "metadata": self.params
        }


class LLMNode(Node):
    """Node for LLM responses."""

    def run(self, input_data: Any) -> Any:
        try:
            from openai import OpenAI
        except ModuleNotFoundError:
            require("OpenAI", "LLM generation", "retrieval")
        client = OpenAI(
            base_url=self.params.get("base_url", "http://localhost:11434/v1"),
            api_key=self.params.get("api_key", "ollama")
        )
        prompt = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = prompt
        
        response = client.chat.completions.create(
            model=self.params.get("model", "llama3"),
            messages=[{"role": "user", "content": prompt}],
            temperature=self.params.get("temperature", 0.7)
        )
        result = response.choices[0].message.content
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"LLM generated response ({len(self._last_output) if self._last_output else 0} chars)",
            "metadata": {"model": self.params.get("model", "llama3")}
        }


class FilterNode(Node):
    """Node for filtering results."""

    def run(self, input_data: Any) -> Any:
        if not isinstance(input_data, list):
            return input_data

        self._last_input = input_data

        filter_fn = self.params.get("filter_fn")
        if filter_fn and callable(filter_fn):
            result = [item for item in input_data if filter_fn(item)]
            self._last_output = result
            return result

        min_score = self.params.get("min_score", 0.0)
        key = self.params.get("key", "score")

        result = [
            item for item in input_data
            if (item.get(key, 0.0) >= min_score if isinstance(item, dict) else True)
        ]
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"Filtered from {len(self._last_input) if isinstance(self._last_input, list) else 0} to {len(self._last_output) if self._last_output else 0} items",
            "metadata": self.params
        }


class RankNode(Node):
    """Node for ranking results."""

    def run(self, input_data: Any) -> Any:
        if not isinstance(input_data, list):
            return input_data

        self._last_input = input_data

        key = self.params.get("key", "final_score")
        reverse = self.params.get("reverse", True)

        result = sorted(input_data, key=lambda x: x.get(key, 0.0), reverse=reverse)
        self._last_output = result
        return result

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"Ranked {len(self._last_output) if self._last_output else 0} items by '{self.params.get('key', 'final_score')}'",
            "metadata": self.params
        }


class QueryAnalysisNode(Node):
    """Node for query analysis."""

    def run(self, input_data: Any) -> Any:
        from .analyzer import QueryAnalyzer
        query = input_data if isinstance(input_data, str) else str(input_data)
        self._last_input = query
        
        result = QueryAnalyzer.analyze(query)
        self._last_output = result.to_dict()
        
        return result.to_dict()

    def explain(self) -> dict:
        return {
            "node_name": self.name,
            "processing_summary": f"Query type: {self._last_output.get('query_type', 'unknown') if self._last_output else 'unknown'}",
            "detected_patterns": self._last_output.get("detected_patterns", []) if self._last_output else [],
            "metadata": {"rewritten_query": self._last_output.get("rewritten_query", "") if self._last_output else ""}
        }


NODE_TYPES = {
    "retrieval": RetrievalNode,
    "bm25": BM25Node,
    "dense": DenseNode,
    "statistical": StatisticalNode,
    "llm": LLMNode,
    "filter": FilterNode,
    "rank": RankNode,
    "query_analyzer": QueryAnalysisNode,
    "analyze": QueryAnalysisNode,
}


class Pipeline:
    """Pipeline for orchestrating retrieval and processing steps.
    
    Usage:
        flow = Pipeline("my-pipeline")
        flow.add_node("retrieval", "statistical", k=5)
        flow.add_node("llm", "llm", model="llama3")
        flow.connect("retrieval", "llm")
        
        # Simple run
        result = flow.run("your query")
        
        # Debug mode
        result = flow.run("your query", debug=True)
        
        # Visual trace
        flow.print_trace()
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._nodes: dict[str, Node] = {}
        self._edges: list[tuple[str, str]] = []
        self._trace: list[TraceEntry] = []
        self._debug_info: dict = {}
        self._original_query: str = ""

    def add_node(self, name: str, node_type: str, **params) -> "Pipeline":
        """Add a node to the pipeline.
        
        Args:
            name: Unique name for this node
            node_type: Type of node (string like "retrieval", "bm25", etc.) OR a Node subclass
            **params: Node-specific parameters
        
        Returns:
            Self for chaining
        """
        if isinstance(node_type, type) and issubclass(node_type, Node):
            self._nodes[name] = node_type(name, **params)
            logger.info(f"Added custom node: {name} (type: {node_type.__name__})")
            return self

        node_class = NODE_TYPES.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")

        self._nodes[name] = node_class(name, **params)
        logger.info(f"Added node: {name} (type: {node_type})")
        return self

    def connect(self, from_node: str, to_node: str) -> "Pipeline":
        """Connect two nodes in the pipeline."""
        if from_node not in self._nodes:
            raise ValueError(f"Unknown source node: {from_node}")
        if to_node not in self._nodes:
            raise ValueError(f"Unknown target node: {to_node}")

        self._edges.append((from_node, to_node))
        logger.info(f"Connected: {from_node} -> {to_node}")
        return self

    def run(self, input_data: Any, debug: bool = False, seed: int = None) -> Any:
        """Run the pipeline on input data.
        
        Args:
            input_data: The query or data to process
            debug: If True, return structured PipelineResult with debug info
            seed: Optional seed for deterministic reproducibility
        
        Returns:
            PipelineResult with query, results, trace, and debug_info
        """
        if seed is not None:
            import random
            random.seed(seed)
            try:
                import numpy as np
            except ModuleNotFoundError:
                require("NumPy", "deterministic seeding")
            np.random.seed(seed)
            logger.info(f"Seed {seed} set for deterministic reproducibility")

        self._trace = []
        self._debug_info = {"query_analysis": {}, "node_details": [], "seed": seed}
        self._original_query = input_data if isinstance(input_data, str) else str(input_data)

        if debug:
            from .analyzer import QueryAnalyzer
            analysis = QueryAnalyzer.analyze(self._original_query)
            self._debug_info["query_analysis"] = {
                "detected_type": analysis.query_type.value,
                "rewritten_query": analysis.rewritten_query,
                "confidence": analysis.confidence,
                "suggested_retrieval": analysis.suggested_retrieval
            }

        if not self._edges:
            output = self._run_linear(input_data)
        else:
            output = self._run_dag(input_data)

        if debug:
            results = self._format_results(output)
        else:
            results = self._format_results(output)

        if not results:
            return PipelineResult(
                query=self._original_query,
                results=[],
                trace=self.trace() if debug else [],
                metadata={"pipeline_name": self.name},
                debug_info=self._debug_info if debug else {},
                debug=debug,
                message="No results found. Try adjusting the query or k parameter."
            )

        return PipelineResult(
            query=self._original_query,
            results=results,
            trace=self.trace() if debug else [],
            metadata={"pipeline_name": self.name},
            debug_info=self._debug_info if debug else {},
            debug=debug
        )

    def _format_results(self, output: Any) -> list:
        """Format output into standardized results list."""
        results = []

        if isinstance(output, list):
            for item in output:
                if hasattr(item, "doc_id"):
                    results.append({
                        "doc_id": item.doc_id,
                        "text": item.text[:200] + "..." if len(item.text) > 200 else item.text,
                        "score": item.final_score,
                        "explanation": {
                            "dense": item.dense_score,
                            "bm25": item.bm25_score,
                            "rule": item.rule_score,
                            "metadata": item.metadata_score
                        }
                    })
                elif isinstance(item, (tuple, list)) and len(item) >= 2:
                    results.append({
                        "doc_id": item[0],
                        "score": item[1]
                    })
                else:
                    results.append({"result": str(item)})

        elif isinstance(output, str):
            results.append({"response": output})

        return results

    def _run_linear(self, input_data: Any) -> Any:
        """Run pipeline linearly (no edges defined)."""
        current = input_data

        for name, node in self._nodes.items():
            logger.info(f"Executing node: {name}")
            output = node.run(current)

            self._trace.append(TraceEntry(
                step=name,
                node_type=node.__class__.__name__,
                input_data=current,
                output_data=output,
                metadata=node.params
            ))

            node_info = node.explain()
            self._debug_info["node_details"].append(node_info)

            current = output

        return current

    def _run_dag(self, input_data: Any) -> Any:
        """Run pipeline as DAG (edges defined)."""
        from collections import defaultdict, deque

        in_degree = defaultdict(int)
        adj = defaultdict(list)

        for from_node, to_node in self._edges:
            adj[from_node].append(to_node)
            in_degree[to_node] += 1

        start_nodes = [n for n in self._nodes.keys() if in_degree[n] == 0]
        if not start_nodes:
            start_nodes = list(self._nodes.keys())[:1]

        results = {start_nodes[0]: input_data}
        queue = deque(start_nodes)

        while queue:
            current_node = queue.popleft()
            node = self._nodes[current_node]
            current_input = results.get(current_node)

            logger.info(f"Executing node: {current_node}")
            output = node.run(current_input)

            self._trace.append(TraceEntry(
                step=current_node,
                node_type=node.__class__.__name__,
                input_data=current_input,
                output_data=output,
                metadata=node.params
            ))

            node_info = node.explain()
            self._debug_info["node_details"].append(node_info)

            for next_node in adj[current_node]:
                if next_node not in results:
                    results[next_node] = output
                else:
                    if isinstance(results[next_node], list) and isinstance(output, list):
                        results[next_node] = results[next_node] + output
                in_degree[next_node] -= 1
                if in_degree[next_node] == 0:
                    queue.append(next_node)

        return output

    def trace(self) -> list[dict]:
        """Return pipeline execution trace."""
        return [
            {
                "step": entry.step,
                "node_type": entry.node_type,
                "metadata": entry.metadata
            }
            for entry in self._trace
        ]

    def print_trace(self) -> None:
        """Print a simple visual trace of the pipeline execution.
        
        Output format:
        [NodeName] -> description
        """
        print(f"\n{'='*50}")
        print(f"Pipeline: {self.name}")
        print(f"{'='*50}")

        if self._debug_info.get("query_analysis"):
            qa = self._debug_info["query_analysis"]
            print(f"[QueryAnalyzer] -> {qa.get('detected_type', 'unknown')}")
            if qa.get("rewritten_query"):
                print(f"  |-- Rewritten: {qa['rewritten_query']}")

        for entry in self._trace:
            node_class = entry.node_type
            step = entry.step

            if "Retrieval" in node_class or "Dense" in node_class or "BM25" in node_class or "Statistical" in node_class:
                output_desc = f"{len(entry.output_data) if isinstance(entry.output_data, list) else 0} docs scored"
            elif "LLM" in node_class:
                output_desc = "response generated"
            elif "Filter" in node_class:
                output_desc = f"filtered"
            elif "Rank" in node_class:
                output_desc = f"top {len(entry.output_data) if isinstance(entry.output_data, list) else 0} selected"
            elif "QueryAnalysis" in node_class:
                output_desc = f"type detected"
            else:
                output_desc = "processed"

            print(f"[{step}] -> {output_desc}")

        print(f"{'='*50}\n")

    def clear(self) -> "Pipeline":
        """Clear all nodes and edges."""
        self._nodes = {}
        self._edges = []
        self._trace = []
        self._debug_info = {}
        return self
