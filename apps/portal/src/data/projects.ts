export type ProjectStatus = "live" | "external" | "planned" | "local-only";
export type DeploymentTarget =
  | "vercel"
  | "streamlit-cloud"
  | "render"
  | "railway"
  | "docker-vps"
  | "local";

export type ProjectCategory =
  | "Prompt Engineering"
  | "Retrieval"
  | "Evaluation"
  | "Tool Calling"
  | "MCP"
  | "Local Agents"
  | "Vector Databases"
  | "Developer Tooling"
  | "Learning Labs";

export type Project = {
  slug: string;
  name: string;
  description: string;
  category: ProjectCategory;
  status: ProjectStatus;
  deploymentTarget: DeploymentTarget;
  stack: string[];
  liveUrl?: string;
  sourceUrl?: string;
  sourcePath: string;
  localOnly: boolean;
  featured?: boolean;
  summary: string;
  deploymentNotes: string;
};

// Configure your GitHub repository here
// Format: https://github.com/{owner}/{repo}
// Leave both empty strings to disable GitHub links
const GITHUB_OWNER = "roomariz";
const GITHUB_REPO = "ai-learning-lab";
const repoBase = GITHUB_OWNER && GITHUB_REPO 
  ? `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/tree/master`
  : "";

// Helper to generate sourceUrl only if repo is configured
const sourceUrl = (path: string): string | undefined => repoBase ? `${repoBase}/${path}` : undefined;

export const projects: Project[] = [
  {
    slug: "prompt-master",
    name: "Prompt Master",
    description:
      "A browser-based prompt optimization interface and reusable skill for adapting prompts across AI tools.",
    category: "Prompt Engineering",
    status: "planned",
    deploymentTarget: "vercel",
    stack: ["Static HTML", "CSS", "JavaScript", "Prompt Engineering"],
    sourceUrl: sourceUrl("projects/prompt-master"),
    sourcePath: "projects/prompt-master",
    localOnly: false,
    featured: true,
    summary:
      "Prompt Master is a lightweight static web app for generating, repairing, and adapting prompts. It is intentionally simple to deploy and does not require secrets or a backend runtime.",
    deploymentNotes:
      "Vercel static deployment from projects/prompt-master. No environment variables are required.",
  },
  {
    slug: "hf-provider-model-scanner",
    name: "HF Provider Model Scanner",
    description:
      "Static report UI for Hugging Face inference-provider model availability, latency, and agentic coding suitability.",
    category: "Evaluation",
    status: "live",
    deploymentTarget: "vercel",
    stack: ["Python", "Static HTML", "CSV", "JSON", "Hugging Face"],
    liveUrl: "https://11-hf-provider-model-scanner.vercel.app/",
    sourceUrl: sourceUrl("projects/11-hf-provider-model-scanner"),
    sourcePath: "projects/11-hf-provider-model-scanner",
    localOnly: false,
    featured: true,
    summary:
      "The deployed surface is a static report viewer only. Scanner execution, provider probing, and token usage stay outside Vercel.",
    deploymentNotes:
      "Vercel publishes generated report artifacts from .vercel-output-static. HF_TOKEN must never be exposed in static output.",
  },
  {
    slug: "query-flow",
    name: "QueryFlow",
    description:
      "Explainable retrieval and query orchestration with deterministic filters, hybrid ranking, and traceable result explanations.",
    category: "Retrieval",
    status: "external",
    deploymentTarget: "streamlit-cloud",
    stack: ["Python", "Streamlit", "BM25", "FAISS", "Retrieval"],
    liveUrl: "https://ai-learning-lab-03-query-flow.streamlit.app/",
    sourceUrl: sourceUrl("projects/03-query-flow"),
    sourcePath: "projects/03-query-flow",
    localOnly: false,
    featured: true,
    summary:
      "QueryFlow is the cleanest public Python demo: a Streamlit UI over an explainable retrieval engine with deterministic and statistical retrieval paths.",
    deploymentNotes:
      "Deploy externally on Streamlit Community Cloud. Do not convert it to Vercel unless the UI is intentionally rewritten later.",
  },
  {
    slug: "rag-benchmark-lab",
    name: "RAG Benchmark Lab",
    description:
      "Dashboard for retrieval testing, ingestion experiments, RAGAS evaluation, embedding comparison, and saved analytics.",
    category: "Evaluation",
    status: "planned",
    deploymentTarget: "render",
    stack: ["Python", "Streamlit", "Qdrant", "RAGAS", "Pandas"],
    sourceUrl: sourceUrl("projects/04-ragas-evaluation"),
    sourcePath: "projects/04-ragas-evaluation",
    localOnly: false,
    featured: true,
    summary:
      "A heavier Streamlit dashboard with vector-store and evaluation dependencies. It belongs on Render or Railway with explicit service configuration.",
    deploymentNotes:
      "Use Render or Railway. Use Qdrant Cloud for public demos and keep local file artifacts out of public builds.",
  },
  {
    slug: "ai-toolkit",
    name: "AI Toolkit",
    description:
      "Tool-calling framework with Streamlit explorer, CLI entrypoints, async execution, retries, and structured tool schemas.",
    category: "Tool Calling",
    status: "planned",
    deploymentTarget: "render",
    stack: ["Python", "Streamlit", "Ollama", "JSON Schema", "Requests"],
    sourceUrl: sourceUrl("projects/08-ai-toolkit"),
    sourcePath: "projects/08-ai-toolkit",
    localOnly: false,
    featured: true,
    summary:
      "The Streamlit UI is deployable, but the current default model path assumes Ollama. Public hosting should either use a remote model API or run on a controlled Docker host.",
    deploymentNotes:
      "Use Render if backed by OpenAI/OpenRouter. Use Docker VPS if preserving Ollama.",
  },
  {
    slug: "tool-calling-agents",
    name: "Tool Calling Agents",
    description:
      "Agent implementations for weather, calculator, medical routing, document QA, memory, persistence, and tool-selection evaluation.",
    category: "Tool Calling",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "LangChain", "LangGraph", "SQLite", "Evaluation"],
    sourceUrl: sourceUrl("projects/02-tool-calling-agents"),
    sourcePath: "projects/02-tool-calling-agents",
    localOnly: true,
    summary:
      "A source-first lab for building and evaluating tool-calling agents. It uses local scripts and agent runtimes rather than a deployable web UI.",
    deploymentNotes:
      "Keep local-only. If a public demo is needed later, wrap a specific workflow behind an authenticated Python service.",
  },
  {
    slug: "rag-engineering-lab",
    name: "RAG Engineering Lab",
    description:
      "Hands-on RAG tutorials covering document loading, chunking, embeddings, retrieval, generation, and LangSmith tracing.",
    category: "Retrieval",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "LangChain", "LangGraph", "Ollama", "LangSmith"],
    sourceUrl: sourceUrl("projects/06-rag-engineering-lab"),
    sourcePath: "projects/06-rag-engineering-lab",
    localOnly: true,
    summary:
      "A local learning lab for RAG pipeline construction. It assumes local Ollama models and script-based exercises.",
    deploymentNotes:
      "Keep local-only unless a specific exercise is converted into a hosted Streamlit or API demo.",
  },
  {
    slug: "ollama-langsmith-react-tracing-agent",
    name: "Ollama LangSmith ReAct Tracing Agent",
    description:
      "Local ReAct-style agent example with Ollama, tool calls, renewable-energy lookup, arithmetic tooling, and LangSmith tracing.",
    category: "Local Agents",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "Ollama", "LangChain", "LangSmith", "ReAct"],
    sourceUrl: sourceUrl("projects/ai-agents/01-ollama-langsmith-react-tracing-agent"),
    sourcePath: "projects/ai-agents/01-ollama-langsmith-react-tracing-agent",
    localOnly: true,
    summary:
      "A local tracing demo for observing agent reasoning, tool calls, and final responses through LangSmith.",
    deploymentNotes:
      "Keep local-only because it depends on local Ollama and developer-owned LangSmith credentials.",
  },
  {
    slug: "ollama-local-agent-tracing",
    name: "Ollama Local Agent Tracing",
    description:
      "Local Ollama agent with structured JSONL traces, custom tools, log rotation, and LangGraph-oriented execution patterns.",
    category: "Local Agents",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "Ollama", "LangChain", "LangGraph", "JSONL"],
    sourceUrl: sourceUrl("projects/ai-agents/02-ollama-local-agent-tracing"),
    sourcePath: "projects/ai-agents/02-ollama-local-agent-tracing",
    localOnly: true,
    summary:
      "A local observability lab for tracing agent behavior without turning the tracing runtime into a public service.",
    deploymentNotes:
      "Keep local-only. Public deployment would require replacing local Ollama and hardening trace storage.",
  },
  {
    slug: "ai-dev-server",
    name: "AI Dev Server",
    description:
      "CLI workflow that generates, validates, runs, and hot-reloads Express backends from natural language prompts.",
    category: "Developer Tooling",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Node.js", "TypeScript", "Express", "OpenAI", "OpenRouter"],
    sourceUrl: sourceUrl("projects/05-ai-dev-server"),
    sourcePath: "projects/05-ai-dev-server",
    localOnly: true,
    summary:
      "This is a developer CLI, not a web UI. Generated Express apps may be deployed separately, but the tool itself remains source/demo oriented.",
    deploymentNotes:
      "Keep local or publish as an npm package. Do not expose generation/runtime controls as a public unauthenticated service.",
  },
  {
    slug: "mcp-cli-project",
    name: "MCP CLI Project",
    description:
      "Command-line chat client that enriches local Ollama responses with MCP tools, prompts, and document resources.",
    category: "MCP",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "MCP", "Ollama", "Prompt Toolkit"],
    sourceUrl: sourceUrl("projects/09-mcp-cli-project"),
    sourcePath: "projects/09-mcp-cli-project",
    localOnly: true,
    summary:
      "A local-first MCP learning project with subprocess server orchestration and local model assumptions.",
    deploymentNotes:
      "Keep local. Public MCP deployments require authentication, sandboxing, and tool-level authorization.",
  },
  {
    slug: "mcp-lab",
    name: "MCP Lab",
    description:
      "LangChain agent wired to a FastMCP math server with local Ollama model selection.",
    category: "MCP",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "FastMCP", "LangChain", "Ollama"],
    sourceUrl: sourceUrl("projects/10-mcp-lab"),
    sourcePath: "projects/10-mcp-lab",
    localOnly: true,
    summary:
      "A focused MCP server/client lab. It has no public web UI and depends on local runtime coordination.",
    deploymentNotes: "Keep as a local source/demo lab.",
  },
  {
    slug: "tracerag",
    name: "TraceRAG",
    description:
      "Citation-first document question answering with sentence-level retrieval, source traceability, and Milvus-backed embeddings.",
    category: "Vector Databases",
    status: "local-only",
    deploymentTarget: "docker-vps",
    stack: ["Python", "Milvus", "Ollama", "PDF", "Retrieval"],
    sourceUrl: sourceUrl("projects/07-milvus-vector-store-lab"),
    sourcePath: "projects/07-milvus-vector-store-lab",
    localOnly: true,
    summary:
      "TraceRAG is a strong architecture demo, but Milvus and Ollama make it unsuitable for Vercel and better suited to Docker/VPS if made public.",
    deploymentNotes:
      "Keep local now. If public later, deploy as a containerized service with managed vector storage or an isolated VPS.",
  },
  {
    slug: "ollama-agent-state-middleware-lab",
    name: "Ollama Agent State & Middleware Lab",
    description:
      "Progressive labs covering agent state, persistence, middleware, authorization, trimming, retries, and cost tracking.",
    category: "Local Agents",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Python", "LangChain", "Ollama", "OpenRouter", "Middleware"],
    sourceUrl: sourceUrl("projects/ollama-agent-state-middleware-lab"),
    sourcePath: "projects/ollama-agent-state-middleware-lab",
    localOnly: true,
    summary:
      "A source-first learning path for production agent controls. Terminal apps and local model assumptions should not be forced onto Vercel.",
    deploymentNotes: "Keep local-only and document prerequisites clearly.",
  },
  {
    slug: "langchain-academy",
    name: "LangChain Academy Experiments",
    description:
      "Notebook and LangGraph Studio experiments for learning LangGraph concepts and deployment patterns.",
    category: "Learning Labs",
    status: "local-only",
    deploymentTarget: "local",
    stack: ["Jupyter", "LangGraph", "LangSmith", "Python"],
    sourceUrl: sourceUrl("projects/langchain-academy"),
    sourcePath: "projects/langchain-academy",
    localOnly: true,
    summary:
      "This is a learning workspace with notebooks and local LangGraph Studio configs, not a standalone hosted web app.",
    deploymentNotes:
      "Keep local or use LangGraph Platform for specific graph deployments.",
  },
];

export const featuredProjects = projects.filter((project) => project.featured);
export const liveProjects = projects.filter((project) => project.status === "live" || project.status === "external");
export const localOnlyProjects = projects.filter((project) => project.localOnly);

export function getProject(slug: string) {
  return projects.find((project) => project.slug === slug);
}

export function getCategories() {
  return Array.from(new Set(projects.map((project) => project.category))).sort();
}
