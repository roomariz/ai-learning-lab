from uuid import uuid4

import streamlit as st

from memory_semantic import (
    add_memory,
    search_memories,
    list_memories,
    delete_memory,
    delete_all_memories,
)
from agent import create_memory_agent, summarise_thread, load_thread_messages


st.set_page_config(page_title="MemorAI Chatbot", page_icon="🧠")


if "thread_keys" not in st.session_state:
    st.session_state.thread_keys = []

if "thread_labels" not in st.session_state:
    st.session_state.thread_labels = {}


with st.sidebar:
    st.header("Chat session")

    current_user = st.text_input("User ID", value="alice")

    if st.session_state.get("active_user") != current_user:
        st.session_state.active_user = current_user
        st.session_state.thread_key = str(uuid4())
        st.session_state.chat_history = []
        st.session_state.pending_memory = None

    if st.session_state.thread_key not in st.session_state.thread_keys:
        st.session_state.thread_keys.append(st.session_state.thread_key)

    if st.button("New conversation"):
        st.session_state.thread_key = str(uuid4())
        st.session_state.chat_history = []
        st.session_state.pending_memory = None
        st.session_state.thread_keys.append(st.session_state.thread_key)
        st.rerun()

    st.caption(f"Thread: `{st.session_state.thread_key[:8]}...`")

    last_user_message = next(
        (
            message["content"]
            for message in reversed(st.session_state.get("chat_history", []))
            if message["role"] == "user"
        ),
        "",
    )

    st.header("Relevant memory")

    stored_items = (
        search_memories(current_user, last_user_message, limit=5)
        if last_user_message
        else []
    )

    if stored_items:
        for item in stored_items:
            st.write(f"- {item}")
    else:
        st.write("_No relevant memories yet._")

    st.header("Manage memory")

    all_memories = list_memories(current_user)

    if all_memories:
        for memory_id, memory_text in all_memories:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"- {memory_text}")

            with col2:
                if st.button("Remove", key=f"remove_{memory_id}"):
                    delete_memory(current_user, memory_id)
                    st.rerun()

        if st.button("Remove all memories"):
            delete_all_memories(current_user)
            st.rerun()
    else:
        st.write("_No saved memories._")

    st.header("Threads")

    for thread_id in st.session_state.thread_keys:
        if thread_id not in st.session_state.thread_labels:
            st.session_state.thread_labels[thread_id] = summarise_thread(thread_id)

        label = st.session_state.thread_labels[thread_id]

        if st.button(
            f"{label} · {thread_id[:8]}",
            key=f"thread_{thread_id}",
        ):
            st.session_state.thread_key = thread_id
            st.session_state.chat_history = load_thread_messages(thread_id)
            st.session_state.pending_memory = None
            st.rerun()


st.title("🧠 MemorAI Chatbot")
st.caption(
    "Ask the assistant to remember something, then approve it before it is "
    "saved to long-term memory."
)

for message in st.session_state.get("chat_history", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if st.session_state.get("chat_history"):
    if st.button("Save whole chat to memory"):
        chat_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in st.session_state.chat_history
        )

        add_memory(
            current_user,
            f"Saved chat conversation:\n{chat_text}",
        )

        st.success("Whole chat saved to memory.")
        st.rerun()


if st.session_state.get("pending_memory"):
    pending = st.session_state.pending_memory

    st.info(f"Save this to long-term memory?\n\n“{pending}”")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save memory"):
            add_memory(current_user, pending)
            st.session_state.pending_memory = None
            st.success("Memory saved.")
            st.rerun()

    with col2:
        if st.button("Do not save"):
            st.session_state.pending_memory = None
            st.info("Memory discarded.")
            st.rerun()


if prompt := st.chat_input("Write your message..."):
    st.session_state.chat_history.append(
        {"role": "user", "content": prompt}
    )

    agent = create_memory_agent(current_user, prompt)

    run_config = {
        "configurable": {
            "thread_id": st.session_state.thread_key
        }
    }

    response = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=run_config,
    )

    assistant_message = response["messages"][-1].content

    proposed_memory = None

    for message in response["messages"]:
        content = getattr(message, "content", "")

        if isinstance(content, str) and "PROPOSE_MEMORY::" in content:
            proposed_memory = content.split("PROPOSE_MEMORY::", 1)[1].strip()
            break

    if proposed_memory:
        st.session_state.pending_memory = proposed_memory
        assistant_message = (
            "I can save this to long-term memory, but I need your approval first:\n\n"
            f"“{proposed_memory}”"
        )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": assistant_message}
    )

    st.session_state.thread_labels[st.session_state.thread_key] = summarise_thread(
        st.session_state.thread_key
    )

    st.rerun()