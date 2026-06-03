import os
import warnings
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import SecretStr
from langchain_cohere import ChatCohere

warnings.filterwarnings("ignore")
load_dotenv()

COHERE_API_KEY = os.environ["COHERE_API_KEY"] 

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set")

llm = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    model="command-a-03-2025",
)

class ArticleState(TypedDict):
    topic: str
    plan: str
    article: str
    edited_article: str


def to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def planner_node(state: ArticleState) -> ArticleState:
    print("\nPlanning article...")
    topic = state["topic"]

    prompt = f"""
You are a Content Planner.

Task:
1. Prioritise the latest trends, key players, and noteworthy news on {topic}.
2. Identify the target audience, considering their interests and pain points.
3. Develop a detailed content outline including an introduction, key points, and a call to action.
4. Include SEO keywords and relevant data or sources.

Expected output:
A comprehensive content plan document with:
- outline;
- audience analysis;
- SEO keywords;
- relevant resources.

Return only the content plan.
"""

    response = llm.invoke(prompt)
    plan_text = to_text(response.content)

    return {
        "topic": topic,
        "plan": plan_text,
        "article": state["article"],
        "edited_article": state["edited_article"],
    }


def writer_node(state: ArticleState) -> ArticleState:
    print("\nWriting article...")
    topic = state["topic"]
    plan = state["plan"]

    prompt = f"""
You are a Content Writer.

Use the content plan below to write a compelling blog post on {topic}.

Content plan:
{plan}

Task:
1. Use the content plan to craft a compelling blog post on {topic}.
2. Incorporate SEO keywords naturally.
3. Name each section and subtitle in an engaging manner.
4. Structure the post with:
   - an engaging introduction;
   - an insightful body; and
   - a summarising conclusion.
5. Proofread for grammar, clarity, and alignment with the brand's voice.

Expected output:
A well-written blog post in markdown format, ready for publication.
Each section should have 2 or 3 paragraphs.

Return only the blog post.
"""

    response = llm.invoke(prompt)
    article_text = to_text(response.content)

    return {
        "topic": topic,
        "plan": plan,
        "article": article_text,
        "edited_article": state["edited_article"],
    }


def editor_node(state: ArticleState) -> ArticleState:
    print("\nEditing article...")
    topic = state["topic"]
    plan = state["plan"]
    article = state["article"]

    prompt = f"""
You are an Editor.

Blog post to edit:
{article}

Task:
Proofread the given blog post for grammatical errors and alignment with the brand's voice.

Expected output:
A well-written blog post in markdown format, ready for publication.
Each section should have 2 or 3 paragraphs.

Additional editing rules:
- Follow journalistic best practice.
- Provide balanced viewpoints where opinions or assertions are made.
- Avoid major controversial topics or opinions where possible.
- Preserve the writer's core meaning.
- Return only the edited blog post.
"""

    response = llm.invoke(prompt)
    edited_text = to_text(response.content)

    return {
        "topic": topic,
        "plan": plan,
        "article": article,
        "edited_article": edited_text,
    }


graph = StateGraph(ArticleState)

graph.add_node("planner", planner_node)
graph.add_node("writer", writer_node)
graph.add_node("editor", editor_node)

graph.set_entry_point("planner")

graph.add_edge("planner", "writer")
graph.add_edge("writer", "editor")
graph.add_edge("editor", END)

article_graph = graph.compile()