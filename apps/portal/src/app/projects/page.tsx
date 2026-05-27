import type { Metadata } from "next";
import Link from "next/link";
import { ProjectGrid } from "@/components/project-grid";
import { Section } from "@/components/section";
import { getCategories, projects } from "@/data/projects";

export const metadata: Metadata = {
  title: "Projects",
  description: "Browse AI Learning Lab projects by deployment status, runtime target, and technical stack.",
};

type Props = {
  searchParams: Promise<{ category?: string }>;
};

export default async function ProjectsPage({ searchParams }: Props) {
  const { category } = await searchParams;
  const categories = getCategories();
  const selectedCategory = category && categories.includes(category as (typeof categories)[number]) ? category : undefined;
  const visibleProjects = selectedCategory ? projects.filter((project) => project.category === selectedCategory) : projects;

  return (
    <Section
      eyebrow="Project index"
      title={selectedCategory ? selectedCategory : "All projects"}
      description="A strict view of what is live, what deploys externally, and what remains local-only by design."
    >
      <div className="mb-6 flex flex-wrap gap-2">
        <Link
          href="/projects"
          aria-current={!selectedCategory ? "page" : undefined}
          className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-sm text-zinc-300 hover:text-white"
        >
          All
        </Link>
        {categories.map((item) => (
          <Link
            key={item}
            href={`/projects?category=${encodeURIComponent(item)}`}
            aria-current={selectedCategory === item ? "page" : undefined}
            className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-sm text-zinc-300 hover:text-white"
          >
            {item}
          </Link>
        ))}
      </div>
      <ProjectGrid projects={visibleProjects} />
    </Section>
  );
}
