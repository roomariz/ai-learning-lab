"""Quick end-to-end retrieval smoke test for QueryFlow."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from query_flow import Dataset, StatisticalRetriever


def main() -> None:
    dataset = Dataset.from_list(
        [
            {"id": "doc_001", "text": "Ada Lovelace was an English mathematician and the first computer programmer."},
            {"id": "doc_002", "text": "Grace Hopper was an American computer scientist who developed the first compiler."},
            {"id": "doc_003", "text": "Marie Curie was a physicist and chemist who discovered radium and polonium."},
        ]
    )

    retriever = StatisticalRetriever(
        use_dense=False,
        use_bm25=False,
        use_rules=True,
        use_metadata=True,
    )
    retriever.set_documents(dataset.documents)

    query = "Find people whose first name starts with A"
    results = retriever.retrieve(query, k=3)

    print("Quick check: end-to-end retrieval")
    print(f"Query: {query}")
    print(f"Documents loaded: {len(dataset)}")
    print(f"Results returned: {len(results)}")

    for result in results:
        print(f"- {result.doc_id}: {result.final_score:.3f} | {result.text}")


if __name__ == "__main__":
    main()
