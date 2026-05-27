import type { DeploymentTarget, ProjectStatus } from "@/data/projects";

export function statusLabel(status: ProjectStatus) {
  const labels: Record<ProjectStatus, string> = {
    live: "Live",
    external: "External demo",
    planned: "Planned",
    "local-only": "Local only",
  };

  return labels[status];
}

export function deploymentLabel(target: DeploymentTarget) {
  const labels: Record<DeploymentTarget, string> = {
    vercel: "Vercel",
    "streamlit-cloud": "Streamlit Cloud",
    render: "Render",
    railway: "Railway",
    "docker-vps": "Docker/VPS",
    local: "Local source",
  };

  return labels[target];
}
