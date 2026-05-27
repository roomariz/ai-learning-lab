import clsx from "clsx";
import type React from "react";
import type { ProjectStatus } from "@/data/projects";
import { statusLabel } from "@/lib/format";

const statusStyles: Record<ProjectStatus, string> = {
  live: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  external: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  planned: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  "local-only": "border-zinc-500/40 bg-zinc-500/10 text-zinc-300",
};

export function StatusBadge({ status }: { status: ProjectStatus }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold",
        statusStyles[status],
      )}
    >
      {statusLabel(status)}
    </span>
  );
}

export function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-xs font-medium text-zinc-300">
      {children}
    </span>
  );
}
