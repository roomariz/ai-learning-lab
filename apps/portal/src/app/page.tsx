import Link from "next/link";
import { GitHubCta } from "@/components/cta";
import { ProjectGrid } from "@/components/project-grid";
import { Section } from "@/components/section";
import type { DeploymentTarget } from "@/data/projects";
import { featuredProjects, getCategories, liveProjects, localOnlyProjects, projects } from "@/data/projects";
import { deploymentLabel } from "@/lib/format";

const stack = [
  "Next.js",
  "Vercel",
  "Streamlit",
  "Python",
  "LangChain",
  "LangGraph",
  "Ollama",
  "Qdrant",
  "Milvus",
  "MCP",
  "OpenAI",
  "Hugging Face",
];

const deploymentHighlights: Array<{ target: DeploymentTarget; text: string }> = [
  {
    target: "vercel",
    text: "Used only for static and Vercel-native web surfaces.",
  },
  {
    target: "streamlit-cloud",
    text: "Best first host for lightweight Streamlit demos.",
  },
  {
    target: "render",
    text: "Preferred for heavier Python dashboards with service dependencies.",
  },
];

export default function HomePage() {
  const categories = getCategories();

  return (
    <>
      <section className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:py-24">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">Runtime-aware AI portfolio</p>
          <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-6xl">
            AI projects deployed where their runtime actually belongs.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-zinc-300">
            A public showcase for RAG, evaluations, tool calling, MCP, local agents, and prompt engineering. Static apps run on
            Vercel, Python dashboards run on Python-native hosts, and local labs stay source-first.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/projects" className="rounded-lg bg-white px-5 py-3 text-sm font-semibold text-zinc-950 transition hover:bg-zinc-200">
              View projects
            </Link>
            <Link
              href="https://github.com/roomariz/ai-learning-lab"
              className="rounded-lg border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.07]"
            >
              GitHub repository
            </Link>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-5 shadow-soft">
          <div className="grid grid-cols-2 gap-3">
            {[
              ["Projects", projects.length.toString()],
              ["Live surfaces", liveProjects.length.toString()],
              ["Local labs", localOnlyProjects.length.toString()],
              ["Categories", categories.length.toString()],
            ].map(([label, value]) => (
              <div key={label} className="rounded-xl border border-white/10 bg-zinc-950/70 p-4">
                <p className="text-3xl font-semibold text-white">{value}</p>
                <p className="mt-1 text-sm text-zinc-400">{label}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-xl border border-white/10 bg-zinc-950/70 p-4">
            <p className="text-sm font-semibold text-white">Deployment model</p>
            <p className="mt-2 text-sm leading-6 text-zinc-400">
              Portal on Vercel. Static apps on Vercel. Streamlit apps on Python hosts. Ollama, MCP, and vector database labs stay local or containerized.
            </p>
          </div>
        </div>
      </section>

      <Section
        eyebrow="Featured"
        title="Featured projects"
        description="The highest-signal demos and source projects from the monorepo."
      >
        <ProjectGrid projects={featuredProjects} />
      </Section>

      <Section
        eyebrow="Live demos"
        title="Public deployment surfaces"
        description="Only projects with a web UI and appropriate runtime are linked as live demos."
      >
        <ProjectGrid projects={liveProjects} />
      </Section>

      <Section
        eyebrow="Local labs"
        title="Source-first experiments"
        description="These projects demonstrate architecture and implementation patterns, but require local runtimes such as Ollama, MCP, Milvus, notebooks, or CLI processes."
      >
        <ProjectGrid projects={localOnlyProjects.slice(0, 6)} />
      </Section>

      <Section
        eyebrow="Learning map"
        title="Learning categories"
        description="The portal keeps project discovery organized by technical domain."
      >
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {categories.map((category) => (
            <Link
              key={category}
              href={`/projects?category=${encodeURIComponent(category)}`}
              className="rounded-xl border border-white/10 bg-white/[0.045] p-4 text-sm font-semibold text-white transition hover:border-sky-300/40 hover:bg-white/[0.065]"
            >
              {category}
            </Link>
          ))}
        </div>
      </Section>

      <Section eyebrow="Stack" title="Technology stack">
        <div className="flex flex-wrap gap-2">
          {stack.map((item) => (
            <span key={item} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-sm text-zinc-300">
              {item}
            </span>
          ))}
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {deploymentHighlights.map((item) => (
            <div key={item.target} className="rounded-xl border border-white/10 bg-white/[0.045] p-5">
              <p className="font-semibold text-white">{deploymentLabel(item.target)}</p>
              <p className="mt-2 text-sm leading-6 text-zinc-400">
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </Section>

      <GitHubCta />
    </>
  );
}
