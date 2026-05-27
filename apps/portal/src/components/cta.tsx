import Link from "next/link";

export function GitHubCta() {
  return (
    <section className="mx-auto max-w-7xl px-5 py-12 sm:px-6 lg:px-8">
      <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-sky-400/14 via-white/[0.055] to-emerald-400/10 p-6 sm:p-8">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-300">Open source</p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            Explore the implementation, deployment boundaries, and local labs.
          </h2>
          <p className="mt-3 text-zinc-300">
            The portal highlights what is live, what belongs on runtime-specific hosting, and what intentionally remains local.
          </p>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="https://github.com/roomariz/ai-learning-lab"
            className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-zinc-950 transition hover:bg-zinc-200"
          >
            View repository
          </Link>
          <Link
            href="/projects"
            className="rounded-lg border border-white/15 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/[0.07]"
          >
            Browse projects
          </Link>
        </div>
      </div>
    </section>
  );
}
