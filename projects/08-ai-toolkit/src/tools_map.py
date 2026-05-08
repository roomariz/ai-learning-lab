"""Tool mappings - maps function names to implementations."""
from functions import search_docs, read_document, summarise_document, extract_keywords, answer_question, get_chuck_norris_fact

tools_map = {
    "search_docs": search_docs,
    "read_document": read_document,
    "summarise_document": summarise_document,
    "extract_keywords": extract_keywords,
    "answer_question": answer_question,
    "get_chuck_norris_fact": get_chuck_norris_fact,
}