import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Pill, StatusBadge } from "@/components/badge";
import { getProject, projects } from "@/data/projects";
import { deploymentLabel } from "@/lib/format";

type Props = {
  params: Promise<{ slug: string }>;
};

export function generateStaticParams() {
  return projects.map((project) => ({ slug: project.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const project = getProject(slug);

  if (!project) {
    return { title: "Project not found" };
  }

  return {
    title: project.name,
    description: project.description,
  };
}

export default async function ProjectDetailPage({ params }: Props) {
  const { slug } = await params;
  const project = getProject(slug);

  if (!project) {
    notFound();
  }

  return (
    <article className="mx-auto max-w-5xl px-5 py-14 sm:px-6 lg:px-8">
      <Link href="/projects" className="text-sm font-medium text-sky-300 hover:text-sky-200">
        Back to projects
      </Link>
      <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.045] p-6 shadow-soft sm:p-8">
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={project.status} />
          <Pill>{deploymentLabel(project.deploymentTarget)}</Pill>
          <Pill>{project.category}</Pill>
          {project.localOnly ? <Pill>Local-only label</Pill> : null}
        </div>
        <h1 className="mt-6 text-3xl font-semibold tracking-tight text-white sm:text-5xl">{project.name}</h1>
        <p className="mt-5 max-w-3xl text-lg leading-8 text-zinc-300">{project.description}</p>

        <div className="mt-8 flex flex-wrap gap-3">
          {project.liveUrl ? (
            <Link href={project.liveUrl} className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-zinc-950 hover:bg-zinc-200">
              Open live demo
            </Link>
          ) : null}
          {project.sourceUrl ? (
            <Link href={project.sourceUrl} className="rounded-lg border border-white/15 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/[0.07]">
              View source
            </Link>
          ) : null}
        </div>
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[0.65fr_0.35fr]">
        <section className="rounded-2xl border border-white/10 bg-white/[0.045] p-6">
          <h2 className="text-xl font-semibold text-white">Architecture notes</h2>
          <p className="mt-3 leading-7 text-zinc-300">{project.summary}</p>
          <h2 className="mt-8 text-xl font-semibold text-white">Deployment guidance</h2>
          <p className="mt-3 leading-7 text-zinc-300">{project.deploymentNotes}</p>
        </section>

        <aside className="rounded-2xl border border-white/10 bg-white/[0.045] p-6">
          <h2 className="text-xl font-semibold text-white">Project metadata</h2>
          <dl className="mt-4 space-y-4 text-sm">
            <div>
              <dt className="text-zinc-500">Source path</dt>
              <dd className="mt-1 font-mono text-zinc-200">{project.sourcePath}</dd>
            </div>
            <div>
              <dt className="text-zinc-500">Deployment target</dt>
              <dd className="mt-1 text-zinc-200">{deploymentLabel(project.deploymentTarget)}</dd>
            </div>
            <div>
              <dt className="text-zinc-500">Stack</dt>
              <dd className="mt-2 flex flex-wrap gap-2">
                {project.stack.map((item) => (
                  <span key={item} className="rounded-md bg-zinc-900 px-2 py-1 text-xs text-zinc-300">
                    {item}
                  </span>
                ))}
              </dd>
            </div>
          </dl>
        </aside>
      </div>
    </article>
  );
}
