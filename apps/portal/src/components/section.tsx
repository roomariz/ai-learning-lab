import type React from "react";

export function Section({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mx-auto max-w-7xl px-5 py-12 sm:px-6 lg:px-8">
      <div className="mb-7 max-w-3xl">
        {eyebrow ? <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-sky-300">{eyebrow}</p> : null}
        <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">{title}</h2>
        {description ? <p className="mt-3 text-base leading-7 text-zinc-400">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
