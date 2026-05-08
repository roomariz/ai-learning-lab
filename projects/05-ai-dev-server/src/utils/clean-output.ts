export function stripMarkdownFences(input: string) {
  return input
    .trim()
    .replace(/```[a-zA-Z]*\n?/g, "")
    .replace(/```/g, "");
}

export function ensureNonEmpty(input: string) {
  const trimmed = input.trim();
  if (!trimmed) {
    throw new Error("Model returned empty output");
  }
  return trimmed;
}
