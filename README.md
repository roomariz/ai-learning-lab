# AI Learning Lab

A clean way to manage this is to treat it like a serious engineering portfolio, not a dumping ground.

Given you are learning AI through hands-on open-source work (RAG, embeddings, interview app, etc.), I would structure it as a mono-repository with strong conventions.

Recommended structure:

```
ai-learning-lab/
│
├── README.md
├── ROADMAP.md
├── PROJECT_INDEX.md
├── requirements/
│   ├── common.txt
│   ├── rag.txt
│   ├── agents.txt
│   └── llm-apps.txt
│
├── docs/
│   ├── architecture/
│   ├── learning-notes/
│   ├── prompts/
│   └── diagrams/
│
├── templates/
│   ├── project-template/
│   ├── experiment-template/
│   └── notebook-template.ipynb
│
├── shared/
│   ├── utils/
│   ├── config/
│   ├── logging/
│   ├── evaluation/
│   └── datasets/
│
├── projects/
│   ├── 01-rag-retrieval-lab/
│   ├── 02-embedding-visualisation/
│   ├── 03-ai-interview-coach/
│   ├── 04-agentic-workflows/
│   ├── 05-fine-tuning-experiments/
│   └── 06-llm-evals/
│
├── notebooks/
│   ├── experiments/
│   └── research/
│
├── tests/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── LICENSE
```

Management strategy:

1. Separate learning by domain

Do not mix everything randomly.

Example:

* `RAG`
* `Agents`
* `Prompt Engineering`
* `LLM Evaluations`
* `Fine-tuning`
* `AI Apps`
* `MLOps`

This makes growth manageable.

---

2. Every project should have the same internal structure

Example:

```
01-rag-retrieval-lab/
├── README.md
├── src/
├── notebooks/
├── tests/
├── data/
├── outputs/
├── prompts/
├── configs/
└── requirements.txt
```

Consistency matters.

---

3. Create a project index

`PROJECT_INDEX.md`

Example:

```markdown
# AI Learning Projects

| Project | Topic | Status | Stack | Notes |
|--------|------|--------|-------|-------|
| RAG Retrieval Lab | Retrieval | Complete | Python, OpenRouter | semantic search |
| Interview Coach | LLM App | In Progress | Streamlit, Python | adaptive interviews |
| Agent Workflow | Agents | Planned | LangGraph | orchestration |
```

This becomes your dashboard.

---

4. Use Git branches properly

Simple model:

```
main        -> stable working code
dev         -> integration branch
feature/*   -> experiments
```

Example:

```bash
feature/rag-faiss
feature/langgraph-agents
feature/evals-framework
```

Never experiment directly in `main`.

---

5. Environment management

AI projects break because dependencies clash.

Use:

```bash
uv
```

or

```bash
poetry
```

instead of raw pip.

Example:

```bash
uv init
uv venv
uv add openai pandas numpy scikit-learn
```

---

6. Secrets management

Never commit:

```
API keys
.env
tokens
credentials
```

Use:

`.env.example`

Example:

```env
OPENROUTER_API_KEY=
OPENAI_API_KEY=
HUGGINGFACE_TOKEN=
```

---

7. Document what you learned

This is the biggest differentiator.

Inside:

```
docs/learning-notes/
```

Example:

```markdown
rag-vs-finetuning.md
embedding-similarity.md
vector-db-comparison.md
agent-memory-patterns.md
```

This turns your repo into a knowledge base.

---

8. Separate reusable code

If you keep rewriting:

* embedding utils
* chunking logic
* evaluation metrics
* prompt helpers

move them into:

```
shared/
```

---

9. CI/CD from day one

Add GitHub Actions:

```
lint
tests
formatting
security scan
```

Example tools:

* black
* ruff
* pytest
* mypy
* bandit

---

10. Naming convention

Bad:

```
test1
newproject
ai-final-final
```

Good:

```
01-rag-retrieval-lab
02-embedding-visualisation
03-ai-interview-coach
```

---

11. Track roadmap

`ROADMAP.md`

Example:

```markdown
## Current Focus
- RAG fundamentals
- vector search
- evaluation metrics

## Next
- LangGraph agents
- MCP tools
- memory systems

## Later
- fine tuning
- multimodal systems
- distributed inference
```

---

12. Public portfolio readiness

For each project include:

* problem statement
* architecture diagram
* setup instructions
* screenshots
* lessons learned
* future improvements

This makes the repo job-ready.

---

Recommended GitHub repo names:

Professional:

* `ai-learning-lab`
* `applied-ai-lab`
* `llm-engineering-lab`
* `ai-systems-playground`

Portfolio style:

* `build-with-ai`
* `ai-engineering-journey`
* `open-ai-projects`

My recommendation:

```
ai-learning-lab
```

Clean and scalable.

For your specific current work, first projects would be:

```
01-rag-retrieval-lab
02-embedding-visualisation
03-ai-interview-coach
04-prompt-engineering-patterns
05-llm-evaluation-suite
```
