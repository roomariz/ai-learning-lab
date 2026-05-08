import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from functions import (
    search_docs,
    read_document,
    summarise_document,
    extract_keywords,
    answer_question,
    get_chuck_norris_fact,
)
from tools_map import tools_map as TOOLS_MAP

TOOL_DISPLAY = {
    "search_docs": ("Search Documentation", search_docs),
    "read_document": ("Read Document", read_document),
    "summarise_document": ("Summarise Document", summarise_document),
    "extract_keywords": ("Extract Keywords", extract_keywords),
    "answer_question": ("Answer Question", answer_question),
    "get_chuck_norris_fact": ("Chuck Norris Fact", get_chuck_norris_fact),
}


def _extract_doc_id(prompt: str) -> str:
    match = re.search(r"\b(\d+)\b", prompt)
    if match:
        return match.group(1)
    return prompt


def _extract_question_and_context(prompt: str) -> tuple[str, str]:
    question_match = re.search(r"question:\s*(.*?)(?:\s+context:\s*(.*))?$", prompt, re.IGNORECASE | re.DOTALL)
    if question_match:
        question = question_match.group(1).strip()
        context = (question_match.group(2) or "").strip()
        return question, context

    context_match = re.search(r"(.*?)(?:\s+context:\s*(.*))$", prompt, re.IGNORECASE | re.DOTALL)
    if context_match:
        return context_match.group(1).strip(), (context_match.group(2) or "").strip()

    return prompt, ""


def _detect_tool_name(prompt: str) -> str | None:
    prompt_lower = prompt.lower()

    if "chuck norris" in prompt_lower and "fact" in prompt_lower:
        return "get_chuck_norris_fact"

    for tool_key in TOOLS_MAP:
        if tool_key.replace("_", " ") in prompt_lower:
            return tool_key

    return None

st.set_page_config(page_title="Tool-Calling CLI", page_icon="🤖")

st.title("🤖 Tool-Calling Framework with Ollama")

mode = st.radio("Mode", ["Interactive", "Tool Explorer"], horizontal=True)

if mode == "Interactive":
    prompt = st.text_area("Enter your prompt:", placeholder="Enter your prompt:")

    if st.button("Run"):
        if prompt:
            with st.spinner("Processing..."):
                st.info("Note: This requires Ollama running locally")

                tool_name = _detect_tool_name(prompt)

                if tool_name:
                    st.success(f"Detected tool: `{tool_name}`")
                    _, tool_func = TOOL_DISPLAY[tool_name]
                    with st.container():
                        st.markdown("---")
                        st.markdown(f"### {tool_name.replace('_', ' ').title()}")
                        if tool_name in {"search_docs", "extract_keywords"}:
                            result = tool_func(prompt)
                        elif tool_name in {"read_document", "summarise_document"}:
                            result = tool_func(_extract_doc_id(prompt))
                        elif tool_name == "answer_question":
                            question, context = _extract_question_and_context(prompt)
                            result = tool_func(question, context)
                        else:
                            result = tool_func()
                        st.json(result)
                else:
                    st.info("No tool detected. Try: 'Search docs for Python' or 'Tell me a Chuck Norris fact'")

else:
    st.markdown("### Available Tools")
    for tool_key, (display_name, _) in TOOL_DISPLAY.items():
        with st.expander(f"🔧 {display_name}"):
            if tool_key == "get_chuck_norris_fact":
                if st.button(f"Run {display_name}", key=tool_key):
                    with st.spinner(f"Running {display_name}..."):
                        _, func = TOOL_DISPLAY[tool_key]
                        result = func()
                        st.json(result)
            elif tool_key == "search_docs":
                query = st.text_input("Search query:", placeholder="Search query:", key=f"{tool_key}_input")
                if st.button(f"Run {display_name}", key=tool_key) and query:
                    with st.spinner(f"Running {display_name}..."):
                        result = search_docs(query)
                        st.json(result)
            elif tool_key == "read_document":
                doc_id = st.text_input("Document ID:", placeholder="Document ID:", key=f"{tool_key}_input")
                if st.button(f"Run {display_name}", key=tool_key) and doc_id:
                    with st.spinner(f"Running {display_name}..."):
                        result = read_document(doc_id)
                        st.json(result)
            elif tool_key == "summarise_document":
                doc_id = st.text_input("Document ID:", placeholder="Document ID:", key=f"{tool_key}_input")
                if st.button(f"Run {display_name}", key=tool_key) and doc_id:
                    with st.spinner(f"Running {display_name}..."):
                        result = summarise_document(doc_id)
                        st.json(result)
            elif tool_key == "extract_keywords":
                text = st.text_area("Text:", placeholder="Text:", key=f"{tool_key}_input")
                if st.button(f"Run {display_name}", key=tool_key) and text:
                    with st.spinner(f"Running {display_name}..."):
                        result = extract_keywords(text)
                        st.json(result)
            elif tool_key == "answer_question":
                question = st.text_input("Question:", placeholder="Question:", key=f"{tool_key}_q")
                context = st.text_area("Context:", placeholder="Context:", key=f"{tool_key}_c")
                if st.button(f"Run {display_name}", key=tool_key) and question:
                    with st.spinner(f"Running {display_name}..."):
                        result = answer_question(question, context)
                        st.json(result)

st.markdown("---")
st.caption("Requires Ollama running at http://localhost:11434")
