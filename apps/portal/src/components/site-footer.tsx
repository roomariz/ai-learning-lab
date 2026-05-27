import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-8 text-sm text-zinc-400 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p>AI Learning Lab. Runtime-aware AI engineering portfolio.</p>
        <div className="flex gap-4">
          <Link className="hover:text-white" href="/projects">
            Projects
          </Link>
          <Link className="hover:text-white" href="/about">
            About
          </Link>
          <Link className="hover:text-white" href="https://github.com/roomariz/ai-learning-lab">
            GitHub
          </Link>
        </div>
      </div>
    </footer>
  );
}
