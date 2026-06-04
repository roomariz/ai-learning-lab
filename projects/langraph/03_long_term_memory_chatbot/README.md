# Long-term Memory Chatbot

A Streamlit-based chatbot that demonstrates semantic long-term memory, thread persistence, memory approval workflows, and conversation checkpoints using LangGraph and Cohere.

## What this project is

* A Streamlit front-end (`app.py`) for chatting with a memory-enabled assistant.
* A Cohere-powered agent (`agent.py`) with tool-calling capabilities.
* Semantic memory retrieval using LangGraph `InMemoryStore` and Cohere embeddings.
* Human-in-the-loop memory approval before any memory is persisted.
* Conversation checkpointing using LangGraph and SQLite (`threads.db`).
* Thread summaries and thread switching.
* Memory management features including listing, deleting, clearing, and saving complete conversations to memory.

## Architecture

```text
User Message
      │
      ▼
LangGraph Agent
      │
      ├── Semantic Memory Search
      │
      ├── Thread Checkpoint Retrieval
      │
      └── Memory Proposal Tool
                 │
                 ▼
         User Approval
                 │
                 ▼
          Memory Store
```

## Main Components

### app.py

Streamlit user interface.

Responsibilities:

* Chat UI
* Thread management
* Memory approval workflow
* Memory administration
* Thread navigation

### agent.py

Agent construction and orchestration.

Responsibilities:

* Cohere model configuration
* Semantic memory injection
* Memory proposal tool
* Thread summarisation
* Checkpoint interaction

### memory_semantic.py

Semantic memory store.

Responsibilities:

* Memory persistence
* Semantic retrieval
* Memory deletion
* Memory administration

### threads.db

SQLite database used by LangGraph for:

* Conversation checkpoints
* Thread state
* Agent state recovery

## Features

### Semantic Memory

Only the most relevant memories are injected into the prompt.

### Human Approval

Memories are proposed by the assistant and require explicit approval before being saved.

### Thread Persistence

Each conversation thread is stored independently and can be revisited later.

### Thread Summaries

Each thread receives a generated summary label for easier navigation.

### Memory Administration

Users can:

* View memories
* Delete individual memories
* Delete all memories
* Save complete conversations as memories

## Requirements

* Python 3.12+
* Cohere API key

Environment variables:

```env
COHERE_API_KEY=your_key_here
```

## Run

```powershell
uv sync
uv run streamlit run app.py
```
