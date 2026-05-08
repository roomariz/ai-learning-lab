import path from "node:path";

export const runtimeConfig = {
  outputDir: path.resolve(process.cwd(), "generated"),
  prompt: "",
  template: "express-basic" as const,
};

export function setRuntimePrompt(prompt: string) {
  runtimeConfig.prompt = prompt;
}

export function setOutputDir(outputDir: string) {
  runtimeConfig.outputDir = path.resolve(process.cwd(), outputDir);
}
