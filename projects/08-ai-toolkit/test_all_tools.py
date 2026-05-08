"""Test all tools with sample parameters."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from functions import (
    search_docs,
    read_document,
    summarise_document,
    extract_keywords,
    answer_question,
    get_chuck_norris_fact,
)

print("Testing all tools...\n")

print("1. search_docs:")
print(search_docs("Python"))

print("\n2. read_document:")
print(read_document("123"))

print("\n3. summarise_document:")
print(summarise_document("456"))

print("\n4. extract_keywords:")
print(extract_keywords("Machine learning and deep learning are popular topics."))

print("\n5. answer_question:")
print(answer_question("What is AI?", "Artificial Intelligence is the simulation of human intelligence."))

print("\n6. get_chuck_norris_fact:")
print(get_chuck_norris_fact())

print("\nAll tests completed!")
