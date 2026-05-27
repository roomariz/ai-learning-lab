# AI Learning Lab Deployment Guide

This repository uses a runtime-aware deployment model.

Do not combine all projects into one application. Static and Vercel-native apps deploy to Vercel. Streamlit/Python apps deploy to Python-friendly hosting. Ollama, MCP, Milvus, notebooks, and CLI projects remain local-only unless explicitly containerized.

## Vercel Deployments

| App | Vercel project | Root directory | Framework preset | Build command | Output directory | Environment variables | Domain |
|---|---|---|---|---|---|---|---|
| Portfolio portal | `ai-learning-lab-portal` | `apps/portal` | Next.js | `npm run build` | `.next` | none initially | `ai-learning-lab.roomariz.dev` |
| Prompt Master | `prompt-master` | `projects/prompt-master` | Other / Static | none | `.` | none | `prompt-master.roomariz.dev` |
| HF Scanner report UI | `hf-model-scanner-report` | repository root | Other / Static | `bash projects/11-hf-provider-model-scanner/build_vercel.sh` | `projects/11-hf-provider-model-scanner/.vercel-output-static` | none for static report | `hf-scanner.roomariz.dev` |

### Portal on Vercel

1. Create a new Vercel project.
2. Import `roomariz/ai-learning-lab`.
3. Set root directory to `apps/portal`.
4. Use the Next.js framework preset.
5. Keep build command as `npm run build`.
6. Keep output directory as `.next`.
7. Add `ai-learning-lab.roomariz.dev`.

### Prompt Master on Vercel

1. Create a separate Vercel project.
2. Import the same repository.
3. Set root directory to `projects/prompt-master`.
4. Use `Other` or static preset.
5. No build command is required.
6. Output directory is `.`.
7. Add `prompt-master.roomariz.dev`.

### HF Scanner Static Report on Vercel

1. Create a separate Vercel project.
2. Import the same repository.
3. Keep root directory as repository root.
4. Use `Other`.
5. Build command:

```bash
bash projects/11-hf-provider-model-scanner/build_vercel.sh
```

6. Output directory:

```text
projects/11-hf-provider-model-scanner/.vercel-output-static
```

7. Add `hf-scanner.roomariz.dev`.

The scanner runtime must not execute on Vercel. Vercel only publishes static report artifacts produced before deployment.

## Streamlit Community Cloud

Use Streamlit Community Cloud for `projects/03-query-flow`.

1. Create a new Streamlit app.
2. Repository: `roomariz/ai-learning-lab`.
3. Branch: `main`.
4. Main file path:

```text
projects/03-query-flow/app.py
```

5. Python dependencies should come from the project manifest. If Streamlit Cloud needs a requirements file, use `projects/03-query-flow/requirements-dev.txt` or add a minimal `requirements.txt` in that folder.
6. Add secrets only in Streamlit Cloud secrets management. Do not commit `.streamlit/secrets.toml`.

Suggested domain:

```text
queryflow.roomariz.dev
```

## Render

Use Render for heavier Streamlit/Python dashboards, especially `projects/04-ragas-evaluation` and optionally `projects/08-ai-toolkit`.

Recommended Render web service settings:

| Setting | RAG Benchmark Lab | AI Toolkit |
|---|---|---|
| Root directory | `projects/04-ragas-evaluation` | `projects/08-ai-toolkit` |
| Runtime | Python | Python |
| Build command | `pip install -r requirements.txt` | `pip install -e .` |
| Start command | `streamlit run src/dashboard/app.py --server.port $PORT --server.address 0.0.0.0` | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |

For RAG Benchmark Lab, use Qdrant Cloud rather than a local Qdrant process.

Suggested domains:

```text
rag-benchmark.roomariz.dev
ai-toolkit.roomariz.dev
```

## Railway

Railway is also valid for Streamlit services when you want faster service setup or attached managed services.

1. Create a Railway project from GitHub.
2. Select `roomariz/ai-learning-lab`.
3. Set the service root directory to the target project.
4. Configure a Python builder.
5. Use the same Streamlit start commands as Render.
6. Add environment variables only to the relevant Railway service.

Use Railway for:

- Streamlit apps that need service-specific environment variables.
- Prototype public demos where deployment velocity matters more than fine-grained infra control.

## Security Hardening

### Secrets

Never commit:

- `HF_TOKEN`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `LANGSMITH_API_KEY`
- `.env`
- `.streamlit/secrets.toml`
- generated local state databases

### HF Scanner Reports

Treat all generated report files as public:

- `reports/*.html`
- `reports/*.json`
- `reports/*.csv`

Before deploying the static report, verify it does not contain:

- tokens
- bearer strings
- private account IDs
- private logs
- internal-only model routing notes

### Environment Segregation

Each deployment gets only the environment variables it needs.

Do not define global secrets for the whole monorepo in Vercel, Render, Railway, or Streamlit Cloud.

### Ollama

Do not expose a local Ollama server publicly. If a public demo must use Ollama, place it behind a controlled Docker/VPS deployment with authentication, rate limits, and network isolation.

### MCP

MCP tools can expose powerful local capabilities. Keep MCP labs local unless they are deployed behind authentication and explicit tool authorization.

## Roadmap

### Phase 1: Fastest Launch

1. Deploy `apps/portal` to Vercel.
2. Deploy `projects/prompt-master` to Vercel.
3. Deploy static HF scanner report UI to Vercel.
4. Mark Streamlit demos as external/planned in the portal.
5. Label local-only labs clearly.

### Phase 2: Public Demos

1. Deploy QueryFlow to Streamlit Community Cloud.
2. Deploy RAG Benchmark Lab to Render or Railway.
3. Decide whether AI Toolkit uses a remote model API or remains Docker/VPS for Ollama.
4. Add final demo URLs to `apps/portal/src/data/projects.ts`.

### Phase 3: Production Polish

1. Add screenshots and preview media to project cards.
2. Add uptime/status badges.
3. Add scheduled HF scanner report generation through GitHub Actions.
4. Add stricter secret scanning and dependency review.
5. Add per-project README deployment badges.
