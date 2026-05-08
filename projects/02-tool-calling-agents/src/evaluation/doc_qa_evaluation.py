"""
Document question-answering evaluation framework.

This module evaluates LLM agents on their ability to answer questions
by selecting and invoking the correct tools over document context.

Supports:
- semantic search with ChromaDB
- deterministic evaluation
- LLM-as-judge evaluation using ragas
- per-difficulty breakdown
- disagreement analysis

Use this to benchmark document QA agents.
"""

import json
import re
import warnings
from collections import defaultdict

import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import chromadb

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory
from ragas import evaluate

warnings.filterwarnings("ignore")

DEFAULT_MODEL = "llama3.1:latest"
DETERMINISTIC_TEMPERATURE = 0

# Step 1: Initialise the language model.
llm = ChatOllama(
    model=DEFAULT_MODEL,
    base_url="http://localhost:11434",
)

print("Checking model...")
response = llm.invoke("Say connection OK")
print(response.content)

# Step 2: Load SQuAD v2 dataset for document context.
print("\nLoading SQuAD v2 dataset...")
dataset = load_dataset("squad_v2", split="validation[:200]")

# Step 3: Initialise embedder and vector store for semantic search.
print("Setting up embedder and vector store...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()

try:
    client.delete_collection("squad_docs")
except:
    pass

collection = client.create_collection("squad_docs")

# Step 4: Index documents for semantic retrieval.
print("Indexing documents...")
for i, item in enumerate(dataset):
    vec = embedder.encode(item["context"]).tolist()

    collection.add(
        ids=[str(i)],
        embeddings=[vec],
        documents=[item["context"]],
        metadatas=[{
            "question": item["question"]
        }]
    )

    if (i + 1) % 50 == 0:
        print(f"  Indexed {i + 1} documents")


# Step 5: Define tools for document assistance.
@tool
def search_context(query: str) -> str:
    """
    Search relevant document context for a factual query.

    Uses semantic similarity to find documents matching
    the query topic.

    Args:
        query:
            The search query (e.g., "theory of relativity").

    Returns:
        JSON string with matching document texts.
    """
    qvec = embedder.encode(query).tolist()

    result = collection.query(
        query_embeddings=[qvec],
        n_results=3
    )

    return json.dumps(result["documents"][0])


@tool
def extract_answer(question: str, context: str) -> str:
    """
    Extract an answer from provided context.

    Uses the LLM to reason over the context and
    extract the answer to the question.

    Args:
        question:
            The question to answer.
        context:
            Document context to search for the answer.

    Returns:
        The extracted answer as a string.
    """
    prompt = f"""
Context:
{context}

Question:
{question}

Return only the answer.
"""

    response = llm.invoke(prompt)
    return response.content


@tool
def summarize_text(text: str) -> str:
    """
    Summarize provided text into key points.

    Args:
        text:
            The text to summarize.

    Returns:
        A summary of the text.
    """
    response = llm.invoke(f"Summarize:\n{text}")
    return response.content


tools = [
    search_context,
    extract_answer,
    summarize_text,
]

# Step 6: Create the agent with tool bindings.
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a document assistant.\n"
        "Use search_context for factual lookup.\n"
        "Use extract_answer when context is provided.\n"
        "Use summarize_text for summaries.\n"
        "Respond directly for casual conversation."
    )
)


# Step 7: Define test cases with varying difficulty.
TestCase = dict

test_cases: list[TestCase] = [
    {
        "query": "Who developed the theory of relativity?",
        "expected_tool": "search_context",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": "Summarize this: Machine learning enables systems to learn patterns.",
        "expected_tool": "summarize_text",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": (
            "Context: Python is a programming language created by Guido van Rossum. "
            "Question: Who created Python?"
        ),
        "expected_tool": "extract_answer",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": "I need to quickly understand this article.",
        "expected_tool": "summarize_text",
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "Can you help me find information about quantum computing?",
        "expected_tool": "search_context",
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "What should I learn to become a data engineer?",
        "expected_tool": None,
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "Hello, how are you?",
        "expected_tool": None,
        "expected_params": None,
        "difficulty": "edge_case",
    },
    {
        "query": "Tell me a joke.",
        "expected_tool": None,
        "expected_params": None,
        "difficulty": "edge_case",
    },
    {
        "query": "What is the capital of France?",
        "expected_tool": "search_context",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": "Summarize the following: The industrial revolution was a period of major industrialization.",
        "expected_tool": "summarize_text",
        "expected_params": None,
        "difficulty": "easy",
    },
]


def extract_tool_calls(response: dict) -> list[dict]:
    """
    Extract tool calls from an agent response.

    Handles both structured tool calls and raw JSON parsing
    from text content.

    Args:
        response:
            Agent response dictionary containing messages.

    Returns:
        List of tool call dictionaries with name and arguments.
    """
    tool_calls = []

    # Structured tool calls from LangChain messages.
    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({"name": tc["name"], "arguments": tc["arguments"]})

    # Fallback: parse raw JSON from content.
    final_msg = None
    for msg in response["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            final_msg = msg
            matches = re.findall(r"\{.*?\}", msg.content, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if "name" in parsed:
                        tool_calls.append({
                            "name": parsed["name"],
                            "arguments": parsed.get("arguments", {})
                        })
                except:
                    pass

    return tool_calls


# Step 8: Run evaluation on all test cases.
print(f"\nRunning evaluation on {len(test_cases)} test cases...")

results = []

for i, case in enumerate(test_cases):
    print(f"\n[{i+1}/{len(test_cases)}] Query: {case['query'][:60]}...")

    response = agent.invoke({
        "messages": [
            {"role": "user", "content": case["query"]}
        ]
    })

    tool_calls = extract_tool_calls(response)

    final_msg = None
    for msg in response["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            final_msg = msg

    if i == 0:
        print(f"  Response messages: {len(response['messages'])}")
        print(f"  Last message type: {final_msg.type if final_msg else 'N/A'}")
        print(f"  Tool calls found: {len(tool_calls)}")
        if tool_calls:
            print(f"  First tool: {tool_calls[0]}")
        print(f"  Raw content: {repr(final_msg.content[:500]) if final_msg and hasattr(final_msg, 'content') and final_msg.content else 'N/A'}")

    actual_tool = tool_calls[0]["name"] if tool_calls else None

    results.append({
        "query": case["query"],
        "expected_tool": case["expected_tool"],
        "actual_tool": actual_tool,
        "tool_correct": actual_tool == case["expected_tool"]
    })


# Step 9: Compute deterministic metrics.
tool_accuracy = sum(
    r["tool_correct"] for r in results
) / len(results)

print(f"\n=== DETERMINISTIC RESULTS ===")
print(f"Tool Accuracy: {tool_accuracy:.2%}")
print(f"Correct: {sum(r['tool_correct'] for r in results)}/{len(results)}")

print("\n=== PER-DIFFICULTY BREAKDOWN ===")
difficulty_groups = defaultdict(list)
for r in results:
    difficulty_groups[r.get("difficulty", "unknown")].append(r)

for difficulty in ["easy", "medium", "edge_case"]:
    group = difficulty_groups.get(difficulty, [])
    if group:
        acc = sum(r["tool_correct"] for r in group) / len(group)
        print(f"  {difficulty}: {acc:.2%} ({sum(r['tool_correct'] for r in group)}/{len(group)})")


# Step 10: LLM-as-judge evaluation.
print("\n=== LLM-AS-JUDGE EVALUATION ===")

metric = DiscreteMetric(
    name="tool_selection",
    allowed_values=["correct", "incorrect"],
    prompt=(
        "Evaluate whether the AI selected the correct tool.\n\n"
        "Tools:\n"
        "- search_context: factual lookup\n"
        "- extract_answer: answer from supplied context\n"
        "- summarize_text: summarise text\n"
        "- NO TOOL: conversational/general advice\n\n"
        "User query: {user_query}\n"
        "Expected tool: {expected_tool}\n"
        "Actual tool: {actual_tool}\n\n"
        "Answer only correct or incorrect."
    ),
)

eval_data = []
for r in results:
    eval_data.append({
        "user_query": r["query"],
        "expected_tool": r["expected_tool"] or "NO TOOL",
        "actual_tool": r["actual_tool"] or "NO TOOL",
    })

eval_df = pd.DataFrame(eval_data)

try:
    eval_result = evaluate(
        eval_df,
        metrics=[metric],
    )

    print(f"LLM Judge Accuracy: {eval_result['tool_selection']:.2%}")
except Exception as e:
    print(f"Judge evaluation failed: {e}")


# Step 11: Disagreement analysis.
print("\n=== DISAGREEMENT ANALYSIS ===")
disagreements = []
for r in results:
    if r["tool_correct"]:
        continue

    expected = r["expected_tool"] or "NO TOOL"
    actual = r["actual_tool"] or "NO TOOL"
    disagreements.append({
        "query": r["query"],
        "expected": expected,
        "actual": actual,
    })

if disagreements:
    print(f"Found {len(disagreements)} disagreement(s):")
    for d in disagreements:
        print(f"  Query: {d['query'][:50]}...")
        print(f"    Expected: {d['expected']} | Actual: {d['actual']}")
else:
    print("No disagreements found - deterministic and judge aligned!")

print("\n=== DONE ===")