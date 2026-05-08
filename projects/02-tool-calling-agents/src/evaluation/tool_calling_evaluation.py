"""
Tool-calling evaluation framework.

This module evaluates LLM agents on their ability to select and invoke
the correct tools for different query types.

Supports:
- deterministic evaluation (exact tool match)
- LLM-as-judge evaluation (using ragas)
- per-difficulty breakdown
- disagreement analysis

Use this to benchmark and improve tool-calling agents.
"""

import json
import re
import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

from datasets import load_dataset
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from sentence_transformers import SentenceTransformer
import chromadb

DEFAULT_MODEL = "qwen2.5-coder:7b"
DOC_SAMPLE_SIZE = 25
DETERMINISTIC_TEMPERATURE = 0

# Step 1: Initialise the language model used for reasoning and tool selection.
llm = ChatOllama(
    model=DEFAULT_MODEL,
    base_url="http://localhost:11434",
    timeout=30,
)

# Step 2: Load a small slice so the script starts quickly.
dataset = load_dataset("hotpot_qa", "distractor", split=f"validation[:{DOC_SAMPLE_SIZE}]")

docs = []
for item in dataset:
    for title, sents in zip(
        item["context"]["title"],
        item["context"]["sentences"]
    ):
        docs.append({
            "title": title,
            "text": " ".join(sents)
        })

# Step 3: Initialise the embedder for semantic search.
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
try:
    client.delete_collection("hotpot_docs")
except:
    pass
collection = client.create_collection("hotpot_docs")

# Step 4: Index documents for semantic retrieval.
for i, doc in enumerate(docs):
    vec = embedder.encode(doc["text"], show_progress_bar=False).tolist()
    collection.add(
        ids=[str(i)],
        embeddings=[vec],
        documents=[doc["text"]],
        metadatas=[{"title": doc["title"]}]
    )


# Step 5: Define tools available to the agent.
@tool
def search_symptoms(symptom: str, duration: str) -> str:
    """
    Search for possible medical conditions matching a symptom and duration.

    Args:
        symptom:
            The symptom to search for (e.g., "headache").
        duration:
            How long the symptom has persisted (e.g., "3 days").

    Returns:
        JSON string with possible conditions and likelihood.
    """
    return json.dumps(
        {
            "conditions": [
                {"condition": "Migraine", "likelihood": "medium"},
                {"condition": "Tension headache", "likelihood": "high"}
            ]
        }
    )


@tool
def suggest_specialist(condition: str, urgency: str) -> str:
    """
    Suggest an appropriate specialist for a medical condition.

    Args:
        condition:
            The medical condition to find a specialist for.
        urgency:
            How urgent the case is ("normal" or "urgent").

    Returns:
        JSON string with specialist recommendation.
    """
    return json.dumps(
        {
            "condition": condition,
            "specialist": "Neurologist",
            "urgency": urgency
        }
    )


@tool
def analyze_medical_report(report_text: str) -> str:
    """
    Analyse a medical report and suggest follow-up actions.

    Args:
        report_text:
            The medical report text to analyse.

    Returns:
        JSON string with risk level and recommendations.
    """
    return json.dumps(
        {
            "risk_level": "moderate",
            "recommendations": [
                "Repeat blood test",
                "Consult physician"
            ]
        }
    )


tools = [
    search_symptoms,
    suggest_specialist,
    analyze_medical_report,
]

print("Creating agent...")
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a medical triage assistant. "
        "Use tools when structured analysis is needed. "
        "For general wellness advice, respond directly."
    )
)
print("Agent created, starting evaluation...")


# Step 6: Define test cases with varying difficulty levels.
TestCase = dict


test_cases: list[TestCase] = [
    # Easy (5 clear cases)
    {
        "query": "I have headaches for 3 days",
        "expected_tool": "search_symptoms",
        "expected_params": {
            "symptom": "headaches",
            "duration": "3 days"
        },
        "difficulty": "easy",
    },
    {
        "query": "Which doctor should I see for suspected migraine?",
        "expected_tool": "suggest_specialist",
        "expected_params": {
            "condition": "migraine",
            "urgency": "normal"
        },
        "difficulty": "easy",
    },
    {
        "query": (
            "Review this report: elevated cholesterol, "
            "borderline glucose, low vitamin D."
        ),
        "expected_tool": "analyze_medical_report",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": "I have a fever and sore throat",
        "expected_tool": "search_symptoms",
        "expected_params": None,
        "difficulty": "easy",
    },
    {
        "query": "Need a cardiologist for heart palpitations",
        "expected_tool": "suggest_specialist",
        "expected_params": None,
        "difficulty": "easy",
    },

    # Medium (4 indirect cases)
    {
        "query": "Been coughing for a week, what could it be?",
        "expected_tool": "search_symptoms",
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "Blood test looks weird, can you check?",
        "expected_tool": "analyze_medical_report",
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "Who handles heart rhythm issues?",
        "expected_tool": "suggest_specialist",
        "expected_params": None,
        "difficulty": "medium",
    },
    {
        "query": "How can I sleep better?",
        "expected_tool": None,
        "expected_params": None,
        "difficulty": "medium",
    },

    # Hard (4 ambiguous cases - for disagreement analysis)
    {
        "query": "Chest pain for 2 days, what should I do?",
        "expected_tool": "search_symptoms",
        "expected_params": None,
        "difficulty": "hard",
    },
    {
        "query": "My blood report looks abnormal, what does it mean and which doctor should I see?",
        "expected_tool": "analyze_medical_report",
        "expected_params": None,
        "difficulty": "hard",
    },
    {
        "query": "I've been feeling anxious lately.",
        "expected_tool": None,
        "expected_params": None,
        "difficulty": "hard",
    },
    {
        "query": "Not sure if my headaches are serious enough to worry about.",
        "expected_tool": "search_symptoms",
        "expected_params": None,
        "difficulty": "hard",
    },

    # Edge (3 no-tool cases)
    {
        "query": "Tell me a joke",
        "expected_tool": None,
        "difficulty": "edge_case",
        "expected_params": None,
    },
    {
        "query": "I'm stressed at work",
        "expected_tool": None,
        "difficulty": "edge_case",
        "expected_params": None,
    },
    {
        "query": "What's the best way to stay healthy?",
        "expected_tool": None,
        "difficulty": "edge_case",
        "expected_params": None,
    },
]


def extract_tool_calls(response: dict) -> list[dict]:
    """
    Extract tool calls from an agent response.

    Handles both structured tool calls (LangChain format) and
    raw JSON parsing from content strings.

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
            tool_calls.extend(msg.tool_calls)

    # Fallback: parse raw JSON tool calls from content.
    if not tool_calls:
        for msg in response["messages"]:
            if hasattr(msg, "content") and isinstance(msg.content, str):
                content = msg.content.strip()

                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and "name" in parsed:
                        tool_calls.append({
                            "name": parsed["name"],
                            "args": parsed.get("arguments", {})
                        })
                except:
                    matches = re.findall(r"\{.*?\}", content, re.DOTALL)
                    for match in matches:
                        try:
                            parsed = json.loads(match)
                            if "name" in parsed:
                                tool_calls.append({
                                    "name": parsed["name"],
                                    "args": parsed.get("arguments", {})
                                })
                        except:
                            pass

    return tool_calls


# Step 7: Run evaluation on all test cases.
results = []

print(f"Running {len(test_cases)} test cases...")

for i, case in enumerate(test_cases):
    print(f"Case {i+1}: {case['query'][:50]}...")
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": case["query"]}
        ]
    })

    tool_calls = extract_tool_calls(response)

    actual_tool = tool_calls[0]["name"] if tool_calls else None
    actual_params = tool_calls[0]["args"] if tool_calls else None

    results.append({
        "query": case["query"],
        "expected_tool": case["expected_tool"],
        "actual_tool": actual_tool,
        "tool_correct": actual_tool == case["expected_tool"]
    })


# Step 8: Compute deterministic metrics.
tool_accuracy = sum(
    r["tool_correct"] for r in results
) / len(results)

print(f"\n=== RESULTS ===")
print(f"Tool Accuracy: {tool_accuracy:.2%}")
print(f"Correct: {sum(r['tool_correct'] for r in results)}/{len(results)}")
print("\nSample results:")
for r in results[:5]:
    print(f"  Query: {r['query'][:60]}...")
    print(f"  Expected: {r['expected_tool']}, Actual: {r['actual_tool']}, Correct: {r['tool_correct']}")
    print()


# Step 9: Set up LLM-as-judge for semantic evaluation.
print("Setting up LLM-as-judge...")

from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory
from openai import OpenAI

judge_llm = llm_factory(
    DEFAULT_MODEL,
    provider="openai",
    client=OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    ),
    temperature=DETERMINISTIC_TEMPERATURE,
)

metric = DiscreteMetric(
    name="tool_selection",
    allowed_values=["correct", "incorrect"],
    prompt=(
        "Evaluate whether the AI agent selected the appropriate tool.\n\n"
        "Available tools:\n"
        "- search_symptoms\n"
        "- suggest_specialist\n"
        "- analyze_medical_report\n"
        "- NO TOOL\n\n"
        "User query: {user_query}\n"
        "Expected tool: {expected_tool}\n"
        "Actual tool selected: {actual_tool}\n\n"
        "Answer only correct or incorrect."
    ),
)

print("Scoring each case with DiscreteMetric...\n")

judge_results = []

for i, r in enumerate(results):
    print(f"Judging case {i+1}/{len(results)}...")

    expected_tool = "NO TOOL" if r["expected_tool"] is None else r["expected_tool"]
    actual_tool = "NO TOOL" if r["actual_tool"] is None else r["actual_tool"]
    score = metric.score(
        llm=judge_llm,
        user_query=r["query"],
        expected_tool=expected_tool,
        actual_tool=actual_tool,
    )

    print(f"  -> {score.value}")

    judge_results.append({
        "value": score.value,
        "reason": score.reason
    })

# Step 10: Compare deterministic vs judge evaluation.
print("\n" + "=" * 70)
print(f"{'Query':<55} {'Det':>5} {'Judge':>7}")
print("-" * 70)

agree_count = 0

for r, j in zip(results, judge_results):
    det = "PASS" if r["tool_correct"] else "FAIL"
    judge = "PASS" if j["value"] == "correct" else "FAIL"

    marker = "  " if det == judge else "!!"

    if det == judge:
        agree_count += 1

    print(f"{marker} {r['query'][:53]:<53} {det:>5} {judge:>7}")

    if det != judge:
        print(f"     Expected: {r['expected_tool']}")
        print(f"     Actual:   {r['actual_tool']}")
        print(f"     Reason:   {j['reason']}")

print(
    f"\nAgreement: {agree_count}/{len(results)} "
    f"({agree_count/len(results):.0%})"
)