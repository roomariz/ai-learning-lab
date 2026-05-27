import Link from "next/link";
import type { Project } from "@/data/projects";
import { deploymentLabel } from "@/lib/format";
import { Pill, StatusBadge } from "./badge";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <article className="group flex h-full flex-col rounded-xl border border-white/10 bg-white/[0.045] p-5 shadow-soft transition hover:-translate-y-0.5 hover:border-sky-300/40 hover:bg-white/[0.065]">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <StatusBadge status={project.status} />
        <Pill>{deploymentLabel(project.deploymentTarget)}</Pill>
        {project.localOnly ? <Pill>Source/demo only</Pill> : null}
      </div>
      <h3 className="text-lg font-semibold text-white">
        <Link href={`/projects/${project.slug}`} className="outline-none focus-visible:ring-2 focus-visible:ring-sky-300">
          {project.name}
        </Link>
      </h3>
      <p className="mt-3 flex-1 text-sm leading-6 text-zinc-400">{project.description}</p>
      <div className="mt-5 flex flex-wrap gap-2">
        {project.stack.slice(0, 5).map((item) => (
          <span key={item} className="rounded-md bg-zinc-900 px-2 py-1 text-xs text-zinc-300">
            {item}
          </span>
        ))}
      </div>
      <div className="mt-6 flex flex-wrap gap-3 text-sm font-medium">
        <Link className="text-sky-300 hover:text-sky-200" href={`/projects/${project.slug}`}>
          Details
        </Link>
        {project.liveUrl ? (
          <Link className="text-emerald-300 hover:text-emerald-200" href={project.liveUrl}>
            Live demo
          </Link>
        ) : null}
        {project.sourceUrl ? (
          <Link className="text-zinc-300 hover:text-white" href={project.sourceUrl}>
            Source
          </Link>
        ) : null}
      </div>
    </article>
  );
}
