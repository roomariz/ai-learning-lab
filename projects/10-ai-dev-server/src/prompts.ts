export const systemPrompt = [
  "You are a precise Node.js assistant.",
  "Generate clean, minimal, production-aware code.",
  "Return only valid JSON that matches the requested schema.",
].join(" ");

export function buildGenerationPrompt(userPrompt: string) {
  return [
    "Create a small Express.js backend project.",
    "Return ONLY valid JSON with this exact shape:",
    '{ "summary": "string", "files": [{ "path": "string", "content": "string" }] }',
    "Rules:",
    "- files must be an array with at least 3 files",
    "- include package.json, src/server.js, and src/app.js",
    "- include src/routes/health.js",
    "- use JavaScript files only",
    "- do not include markdown fences, commentary, or code blocks",
    "- do not omit any required file",
    "",
    `User request: ${userPrompt}`,
  ].join("\n");
}

export function buildRefinePrompt(userPrompt: string, projectSnapshot: string) {
  return [
    "Refine the existing Express.js project.",
    "Return ONLY valid JSON with this exact shape:",
    '{ "summary": "string", "files": [{ "path": "string", "content": "string" }] }',
    "Rules:",
    "- preserve the current project structure unless the request requires changes",
    "- update only the files needed to satisfy the request",
    "- include complete file contents for every file in the response",
    "- do not include markdown fences, commentary, or code blocks",
    "",
    "Current project snapshot:",
    projectSnapshot,
    "",
    `Refinement request: ${userPrompt}`,
  ].join("\n");
}
