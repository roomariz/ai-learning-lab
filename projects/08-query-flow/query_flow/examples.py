"""Killer Examples - Showcasing QueryFlow's capabilities.

This module contains examples that demonstrate the power of explainable retrieval.
"""

from typing import Optional
from .pipeline import Pipeline


LEGAL_DOCUMENTS = [
    {"id": "case_001", "text": "R v. Smith (1995) - UK Court of Appeal case regarding murder conviction in London."},
    {"id": "case_002", "text": "Johnson v. Williams (2018) - US Supreme Court decision on asylum law, held that fear of persecution must be well-founded."},
    {"id": "case_003", "text": "Khan v. UK (2003) - European Court of Human Rights case on deportation to Pakistan due to terrorism concerns."},
    {"id": "case_004", "text": "Ahmed v. Germany (2015) - German Federal Court case on asylum seeker rights and family reunification."},
    {"id": "case_005", "text": "Singh v. Canada (2017) - Canadian Immigration Board ruling on refugee claims from Afghanistan."},
    {"id": "case_006", "text": "R v. Jones (2009) - UK High Court case on criminal sentencing guidelines for assault."},
    {"id": "case_007", "text": "Migration Act Section 501 - Australian law regarding character tests for visa holders."},
    {"id": "case_008", "text": "Patel v. UK (2020) - UK tribunal decision on human rights appeals for Pakistani asylum seekers."},
    {"id": "case_009", "text": "Brown v. USA (2012) - US Federal Court case on constitutional rights in criminal procedure."},
    {"id": "case_010", "text": "European Court of Human Rights - Protocol 4 regarding collective expulsion of aliens."},
]


def run_legal_search_example():
    """Run the killer legal search example.
    
    Query: "Find cases not decided in UK but relevant to asylum law"
    
    This demonstrates:
    - Query type detection (logical)
    - Query rewriting
    - Explainable scoring
    - Why UK cases were excluded
    """
    from .query_flow import set_documents, retrieve_smart
    from .analyzer import QueryAnalyzer
    from .retrieval import StatisticalRetriever

    print("\n" + "="*60)
    print("KILLER EXAMPLE: Explainable Legal Search")
    print("="*60)

    query = "Find cases not decided in UK but relevant to asylum law"
    print(f"\nUser Query: {query}")

    set_documents(LEGAL_DOCUMENTS)

    print("\n" + "-"*40)
    print("STEP 1: Query Analysis")
    print("-"*40)
    analysis = QueryAnalyzer.analyze(query)
    print(f"Detected Type: {analysis.query_type.value}")
    print(f"Confidence: {analysis.confidence:.2f}")
    print(f"Suggested Retrieval: {analysis.suggested_retrieval}")

    print("\n" + "-"*40)
    print("STEP 2: Statistical Retrieval")
    print("-"*40)
    retriever = StatisticalRetriever(use_dense=True, use_bm25=True, use_rules=True, use_metadata=True)
    results = retriever.retrieve(query, k=5)

    print(f"Retrieved {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.doc_id}: {r.text[:70]}...")
        print(f"   Final Score: {r.final_score:.4f}")
        print(f"   Scores: dense={r.dense_score:.3f}, bm25={r.bm25_score:.3f}")

    print("\n" + "-"*40)
    print("STEP 3: Full Explanation")
    print("-"*40)
    explanations = retriever.explain(query, k=5)
    for exp in explanations:
        print(f"\n{doc_id}: {exp['reason']}")
        print(f"  Scores: {exp['scores']}")

    print("\n" + "="*60)
    print("KEY INSIGHT: QueryFlow correctly identifies non-UK cases")
    print("because it detects 'not' as a logical query type and")
    print("uses dense retrieval with semantic matching, not just")
    print("keyword matching.")
    print("="*60 + "\n")

    return results


def run_pipeline_example():
    """Run the pipeline example with debug mode."""
    from .pipelines import rag, statistical
    from .query_flow import set_documents

    set_documents(LEGAL_DOCUMENTS)

    print("\n" + "="*60)
    print("PIPELINE EXAMPLE: RAG with Debug Mode")
    print("="*60)

    query = "asylum law cases in Europe"

    pipeline = rag(k=3)
    result = pipeline.run(query, debug=True)

    print(f"\nQuery: {query}")
    print(f"\nPipeline: {result.metadata['pipeline_name']}")

    print("\n--- Debug Info ---")
    print(f"Query Type: {result.debug_info['query_analysis']['detected_type']}")
    print(f"Rewritten: {result.debug_info['query_analysis']['rewritten_query']}")

    print("\n--- Visual Trace ---")
    pipeline.print_trace()

    print("\n--- Results ---")
    for r in result.results[:3]:
        print(f"  {r.get('doc_id', 'N/A')}: score={r.get('score', 0):.3f}")

    return result


def run_custom_node_example():
    """Example showing how to create a custom node."""
    from .pipeline import Node

    class CustomScorerNode(Node):
        """Custom node that applies domain-specific scoring."""
        
        def __init__(self, name: str, **params):
            super().__init__(name, **params)
            self.boost_terms = params.get("boost_terms", [])

        def run(self, input_data: Any) -> Any:
            """Apply custom scoring logic."""
            if not isinstance(input_data, list):
                return input_data

            boosted = []
            for item in input_data:
                score = item.get("score", 0)
                text = item.get("text", "").lower()

                for term in self.boost_terms:
                    if term.lower() in text:
                        score *= 1.5

                boosted.append({**item, "score": score})

            return sorted(boosted, key=lambda x: x["score"], reverse=True)

        def explain(self) -> dict:
            return {
                "node_name": self.name,
                "processing_summary": f"Applied custom scoring with boost terms: {self.boost_terms}",
                "metadata": self.params
            }

    print("\n" + "="*60)
    print("CUSTOM NODE EXAMPLE")
    print("="*60)
    print("Custom nodes can be created by subclassing Node")
    print("and implementing run() and explain() methods.")
    print("="*60 + "\n")


def run_all_examples():
    """Run all examples."""
    run_legal_search_example()
    run_pipeline_example()
    run_custom_node_example()


if __name__ == "__main__":
    run_all_examples()