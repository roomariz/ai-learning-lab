import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About",
  description: "About the AI Learning Lab monorepo and its runtime-aware deployment strategy.",
};

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-5 py-14 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">About</p>
      <h1 className="mt-5 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
        A monorepo showcase built around honest deployment boundaries.
      </h1>
      <div className="mt-8 space-y-6 text-lg leading-8 text-zinc-300">
        <p>
          AI Learning Lab collects hands-on projects across retrieval, evaluation, tool calling, MCP, local agents, prompt engineering,
          and vector databases. The portal is intentionally not a monolithic app. Each project is deployed according to its runtime.
        </p>
        <p>
          Static and Vercel-native web surfaces go to Vercel. Streamlit dashboards go to Python-friendly hosts. Ollama, MCP, Milvus,
          notebooks, and CLI labs remain source-first unless they are deliberately containerized.
        </p>
      </div>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link href="/projects" className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-zinc-950 hover:bg-zinc-200">
          Browse projects
        </Link>
        <Link
          href="https://github.com/roomariz/ai-learning-lab"
          className="rounded-lg border border-white/15 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/[0.07]"
        >
          View GitHub
        </Link>
      </div>
    </div>
  );
}
