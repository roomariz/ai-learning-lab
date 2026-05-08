"""Reusable function implementations."""
import json
import requests


def search_docs(query: str) -> str:
    """Search documentation for a topic."""
    import re
    patterns = [
        r'search\s+(?:docs?\s+)?(?:for\s+)?(.+)',
        r'find\s+(?:docs?\s+)?(?:about\s+)?(.+)',
        r'lookup\s+(.+)',
    ]
    extracted = query
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip().rstrip('.')
            break

    results = {
        "query": extracted,
        "results": [
            {"title": f"Introduction to {extracted}", "summary": f"Basic overview of {extracted}", "url": f"https://docs.example.com/{extracted.lower().replace(' ', '-')}/intro"},
            {"title": f"{extracted} Guide", "summary": f"Complete guide to {extracted}", "url": f"https://docs.example.com/{extracted.lower().replace(' ', '-')}/guide"},
        ]
    }
    return json.dumps(results)


def read_document(doc_id: str) -> str:
    """Read a document by its ID."""
    doc = {
        "id": doc_id,
        "title": f"Document {doc_id}",
        "content": f"This is the full content of document {doc_id}. It contains detailed information about the topic.",
        "source": f"docs/doc_{doc_id}.md"
    }
    return json.dumps(doc)


def summarise_document(doc_id: str) -> str:
    """Summarise the content of a document."""
    summary = {
        "id": doc_id,
        "title": f"Summary of Document {doc_id}",
        "summary": f"Main points of document {doc_id}: 1) Key concept, 2) Important detail, 3) Conclusion",
        "word_count": 150
    }
    return json.dumps(summary)


def extract_keywords(text: str) -> str:
    """Extract keywords from text."""
    keywords = {
        "text": text[:50] + "...",
        "keywords": ["keyword1", "keyword2", "keyword3"],
        "count": 3
    }
    return json.dumps(keywords)


def answer_question(question: str, context: str) -> str:
    """Answer a question based on the provided context."""
    answer = {
        "question": question,
        "answer": f"Based on the provided context: {context[:50]}...",
        "confidence": 0.85
    }
    return json.dumps(answer)


def get_chuck_norris_fact() -> str:
    """Get a random Chuck Norris fact from an external API."""
    response = requests.get("https://api.chucknorris.io/jokes/random")
    response.raise_for_status()
    data = response.json()
    return json.dumps({
        "fact": data["value"],
        "id": data["id"],
        "url": data["url"]
    })