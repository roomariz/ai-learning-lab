import os
import json
from dotenv import load_dotenv
from typing import Literal
from typing_extensions import TypedDict, NotRequired, Any, Mapping
from pydantic import SecretStr

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")


llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct:free",
    api_key=SecretStr(OPENROUTER_API_KEY),
    base_url="https://openrouter.ai/api/v1",
)


class EmailState(TypedDict):
    email: str
    category: NotRequired[str]
    confidence: NotRequired[float]
    reply: NotRequired[str]
    action: NotRequired[str]


def to_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def classify_email(state: EmailState) -> dict:
    """Classify the email and return a confidence score."""

    prompt = (
        "Classify the following customer email.\n"
        "Return only valid JSON in this exact format:\n"
        '{"category": "complaint|enquiry|appreciation|spam", "confidence": 0.0}\n\n'
        "Rules:\n"
        "- Use spam for irrelevant, promotional, abusive, or off-topic text.\n"
        "- confidence must be between 0 and 1.\n\n"
        f"Email: {state['email']}"
    )

    try:
        response = llm.invoke(prompt)
        data = json.loads(to_text(response.content))

        category = str(data.get("category", "enquiry")).lower()
        confidence = float(data.get("confidence", 0.0))

    except Exception:
        category = "enquiry"
        confidence = 0.0

    if category not in {"complaint", "enquiry", "appreciation", "spam"}:
        category = "enquiry"

    confidence = max(0.0, min(confidence, 1.0))

    return {
        "category": category,
        "confidence": confidence,
    }


def flag_spam(state: EmailState) -> dict:
    """Flag spam or irrelevant email without drafting a reply."""

    print(f"SPAM FLAGGED: {state['email']}")

    return {
        "action": "flagged_as_spam",
        "reply": "No reply drafted because this email appears to be spam or irrelevant.",
    }


def flag_for_human(state: EmailState) -> dict:
    """Flag low-confidence classification for human review."""

    print(
        f"HUMAN REVIEW REQUIRED: "
        f"category={state.get('category')}, "
        f"confidence={state.get('confidence')}, "
        f"email={state['email']}"
    )

    return {
        "action": "flagged_for_human_review",
        "reply": "No automatic reply drafted because classification confidence is too low.",
    }

def draft_complaint_reply(state: EmailState) -> dict:
    """Draft a polite reply to a complaint."""

    prompt = (
        "Write a professional reply to this customer enquiry. "
        "Do not invent facts or availability information. "
        "If the answer is unknown, acknowledge the enquiry and "
        "state that the team will confirm the details. "
        "Keep it to 2-3 sentences.\n\n"
        f"Email: {state['email']}"
    )

    response = llm.invoke(prompt)
    return {"reply": to_text(response.content)}


def draft_enquiry_reply(state: EmailState) -> dict:
    """Draft a helpful reply to an enquiry."""

    prompt = (
        "Write a short, helpful reply to this customer enquiry. "
        "Answer in a professional tone. Keep it to 2-3 sentences.\n\n"
        f"Email: {state['email']}"
    )

    response = llm.invoke(prompt)
    return {"reply": to_text(response.content)}

def safe_llm_invoke(prompt: str) -> str:
    try:
        response = llm.invoke(prompt)
        return to_text(response.content)
    except Exception as error:
        if "429" in str(error):
            return (
                "LLM rate limit reached. Please try again later, "
                "or use a paid/stable OpenRouter model."
            )

        return f"LLM call failed: {error}"

def draft_appreciation_reply(state: EmailState) -> dict:
    """Draft a warm reply to appreciation."""

    prompt = (
        "Write a short, warm thank-you reply to this customer appreciation email. "
        "Keep it to 2-3 sentences.\n\n"
        f"Email: {state['email']}"
    )

    return {"reply": safe_llm_invoke(prompt)}

def route_by_category(
    state: EmailState,
) -> Literal[
    "draft_complaint_reply",
    "draft_enquiry_reply",
    "draft_appreciation_reply",
    "flag_spam",
    "flag_for_human",
]:

    category = state.get("category", "enquiry")
    confidence = state.get("confidence", 0.0)

    if category == "spam":
        return "flag_spam"

    if confidence < 0.7:
        return "flag_for_human"

    if category == "complaint":
        return "draft_complaint_reply"

    if category == "appreciation":
        return "draft_appreciation_reply"

    return "draft_enquiry_reply"


graph = StateGraph(EmailState)

graph.add_node("classify_email", classify_email)
graph.add_node("draft_complaint_reply", draft_complaint_reply)
graph.add_node("draft_enquiry_reply", draft_enquiry_reply)
graph.add_node("draft_appreciation_reply", draft_appreciation_reply)
graph.add_node("flag_spam", flag_spam)
graph.add_node("flag_for_human", flag_for_human)

graph.add_edge(START, "classify_email")

graph.add_conditional_edges(
    "classify_email",
    route_by_category,
    [
        "draft_complaint_reply",
        "draft_enquiry_reply",
        "draft_appreciation_reply",
        "flag_spam",
        "flag_for_human",
    ],
)

graph.add_edge("draft_complaint_reply", END)
graph.add_edge("draft_enquiry_reply", END)
graph.add_edge("draft_appreciation_reply", END)
graph.add_edge("flag_spam", END)
graph.add_edge("flag_for_human", END)

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()

with open("email_response_graph.png", "wb") as file:
    file.write(png_data)

png_path = "email_response_graph.png"
print("Graph saved as email_response_graph.png")

def print_result(email: str, result: Mapping[str, Any]) -> None:
    print("\n" + "=" * 70)
    print(f"Email      : {email[:100]}...")
    print(f"Category   : {result.get('category')}")
    print(f"Confidence : {result.get('confidence')}")
    print(f"Action     : {result.get('action', 'auto_reply_drafted')}")
    print(f"Reply      : {result.get('reply')}")
    print("=" * 70)

def main():
    print("Customer Email Auto-Responder running...")
    print("OPENROUTER_API_KEY loaded:", bool(OPENROUTER_API_KEY))
    print("Graph compiled successfully.")

    sample_emails = [
        "I am very unhappy because my order arrived late and one item was missing.",
        "Could you please confirm whether this product is available in a larger size?",
        "Thank you for the excellent service. The support team was very helpful.",
        "WIN A FREE IPHONE NOW!!! Click this link to claim your prize immediately.",
    ]

    while True:
        print("\nSelect an option:")
        print("1. Use sample email")
        print("2. Type your own email")
        print("3. Show graph")
        print("q. Exit")

        choice = input("\nChoice > ").strip().lower()

        if choice == "q":
            print("Exiting Customer Email Auto-Responder.")
            break

        elif choice == "1":
            print("\nSample emails:")
            for index, email in enumerate(sample_emails, start=1):
                print(f"{index}. {email}")

            selected = input("\nSelect sample number > ").strip()

            if not selected.isdigit():
                print("Please enter a valid number.")
                continue

            selected_index = int(selected) - 1

            if selected_index < 0 or selected_index >= len(sample_emails):
                print("Invalid sample number.")
                continue

            email = sample_emails[selected_index]
            result = app.invoke({"email": email})
            print_result(email, result)

        elif choice == "2":
            email = input("\nCustomer email > ").strip()

            if not email:
                print("Please enter an email.")
                continue

            result = app.invoke({"email": email})
            print_result(email, result)

        elif choice == "3":
            png_path = "email_response_graph.png"

            with open(png_path, "wb") as file:
                file.write(app.get_graph().draw_mermaid_png())

            os.startfile(png_path)
            print("Graph opened and saved as email_response_graph.png")
            print(app.get_graph().draw_ascii())

        else:
            print("Invalid option. Please select 1, 2, 3, or q.")