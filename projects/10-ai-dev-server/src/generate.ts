import OpenAI from "openai";
import fs from "node:fs";
import path from "node:path";
import { ensureDir, removeDir, runCommand, snapshotProject, writeTextFile } from "./utils/files.js";
import { buildGenerationPrompt, buildRefinePrompt, systemPrompt } from "./prompts.js";
import { ensureNonEmpty, stripMarkdownFences } from "./utils/clean-output.js";
import type { GenerateRequest, GenerationResult } from "./types.js";
import { runtimeConfig } from "./runtime.js";

interface ModelFile {
  path: string;
  content: string;
}

interface ModelPayload {
  summary: string;
  files: ModelFile[];
}

export function parseAndValidateGeneration(raw: string, outputDir = runtimeConfig.outputDir): GenerationResult {
  const trimmed = raw.trim();
  const firstBrace = trimmed.indexOf("{");
  const lastBrace = trimmed.lastIndexOf("}");

  if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
    throw new Error("Model did not return valid JSON");
  }

  const jsonText = trimmed.slice(firstBrace, lastBrace + 1);
  const payload = JSON.parse(jsonText) as unknown;

  if (!payload || typeof payload !== "object") {
    throw new Error("Model output must be a JSON object");
  }

  const record = payload as Record<string, unknown>;
  const summary = record.summary;
  const files = record.files;

  if (typeof summary !== "string" || !summary.trim()) {
    throw new Error("Model output must include a non-empty summary string");
  }

  if (!Array.isArray(files) || files.length < 3) {
    throw new Error("Model output must include at least 3 files");
  }

  const validatedFiles = files.map((file) => {
    if (!file || typeof file !== "object") {
      throw new Error("Each file entry must be an object");
    }

    const entry = file as Record<string, unknown>;
    const filePath = entry.path;
    const content = entry.content;

    if (typeof filePath !== "string" || !filePath.trim()) {
      throw new Error("Each file entry must include a non-empty path");
    }

    if (typeof content !== "string") {
      throw new Error(`File ${filePath} must include string content`);
    }

    const normalizedPath = filePath.replace(/\\/g, "/");
    if (path.isAbsolute(normalizedPath) || normalizedPath.startsWith("..") || normalizedPath.includes("../")) {
      throw new Error(`File path must stay within the project root: ${filePath}`);
    }

    return {
      path: normalizedPath.replace(/^\.\/+/, ""),
      content,
    };
  });

  const requiredPaths = ["package.json", "src/server.js", "src/app.js", "src/routes/health.js"];
  for (const requiredPath of requiredPaths) {
    if (!validatedFiles.some((file) => file.path === requiredPath)) {
      throw new Error(`Model output is missing required file: ${requiredPath}`);
    }
  }

  const packageJson = validatedFiles.find((file) => file.path === "package.json");
  if (!packageJson) {
    throw new Error("Model output is missing package.json");
  }

  try {
    const parsedPackage = JSON.parse(packageJson.content) as Record<string, unknown>;
    const scripts = parsedPackage.scripts as Record<string, unknown> | undefined;
    const dependencies = parsedPackage.dependencies as Record<string, unknown> | undefined;

    if (parsedPackage.type !== "module") {
      throw new Error("package.json must use type=module");
    }

    if (typeof scripts?.start !== "string" || !scripts.start.trim()) {
      throw new Error("package.json must include a start script");
    }

    if (typeof dependencies?.express !== "string" || !dependencies.express.trim()) {
      throw new Error("package.json must include express in dependencies");
    }
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Invalid package.json content: ${error.message}`);
    }

    throw new Error("Invalid package.json content");
  }

  return {
    outputDir,
    summary: summary.trim(),
    files: validatedFiles,
  };
}

function normalizeFiles(files: ModelFile[]) {
  const map = new Map(files.map((file) => [file.path, file]));

  return [...map.values()];
}

function repairGenerationPayload(raw: string): string | null {
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const summary = typeof parsed.summary === "string" ? parsed.summary : "Generated backend files.";
    const files = Array.isArray(parsed.files) ? parsed.files : null;

    if (!files) {
      return null;
    }

    const repairedFiles = files.map((file) => {
      if (!file || typeof file !== "object") {
        return file;
      }

      const entry = { ...(file as Record<string, unknown>) };

      if (entry.path === "package.json" && typeof entry.content === "string") {
        try {
          const pkg = JSON.parse(entry.content) as Record<string, unknown>;
          const scripts = (pkg.scripts as Record<string, unknown> | undefined) ?? {};
          const dependencies = (pkg.dependencies as Record<string, unknown> | undefined) ?? {};

          pkg.type = "module";
          if (typeof scripts.start !== "string" || !scripts.start.trim()) {
            scripts.start = "node src/server.js";
          }
          if (typeof dependencies.express !== "string" || !dependencies.express.trim()) {
            dependencies.express = "^4.21.2";
          }

          pkg.scripts = scripts;
          pkg.dependencies = dependencies;
          entry.content = JSON.stringify(pkg, null, 2);
        } catch {
          return file;
        }
      }

      return entry;
    });

    return JSON.stringify({ summary, files: repairedFiles });
  } catch {
    return null;
  }
}

function parseGenerationResult(raw: string): GenerationResult {
  try {
    return parseAndValidateGeneration(raw);
  } catch (error) {
    if (!(error instanceof Error) || !/package\.json/.test(error.message)) {
      throw error;
    }

    const repaired = repairGenerationPayload(raw);
    if (!repaired) {
      throw error;
    }

    return parseAndValidateGeneration(repaired);
  }
}

function normalizeServerContent(filePath: string, content: string) {
  if (filePath === "package.json") {
    try {
      const pkg = JSON.parse(content) as Record<string, unknown>;
      const scripts = (pkg.scripts as Record<string, unknown> | undefined) ?? {};

      pkg.type = "module";
      pkg.main = "src/server.js";
      scripts.start = "node src/server.js";
      pkg.scripts = scripts;

      return JSON.stringify(pkg, null, 2);
    } catch {
      return content;
    }
  }

  if (filePath === "src/server.js") {
    return [
      'import { createApp } from "./app.js";',
      "",
      "const app = createApp();",
      "const port = Number(process.env.PORT || 3000);",
      "",
      "app.listen(port, () => {",
      '  console.log(`Server is running on http://localhost:${port}`);',
      "});",
      "",
    ].join("\n");
  }

  if (filePath === "src/app.js") {
    return [
      'import express from "express";',
      'import { registerHealthRoute } from "./routes/health.js";',
      "",
      "export function createApp() {",
      "  const app = express();",
      "",
      "  registerHealthRoute(app);",
      "",
      '  app.get("/", (_req, res) => {',
      '    res.send("Hello World");',
      "  });",
      "",
      "  return app;",
      "}",
      "",
    ].join("\n");
  }

  if (filePath === "src/routes/health.js") {
    return [
      "export function registerHealthRoute(app) {",
      '  app.get("/health", (_req, res) => {',
      '    res.json({ status: "ok" });',
      "  });",
      "}",
      "",
    ].join("\n");
  }

  return content;
}

function getClient() {
  const useOpenRouter = Boolean(process.env.OPENROUTER_API_KEY);

  return new OpenAI({
    apiKey: useOpenRouter
      ? process.env.OPENROUTER_API_KEY
      : process.env.OPENAI_API_KEY,
    baseURL: useOpenRouter
      ? process.env.OPENROUTER_BASE_URL || "https://openrouter.ai/api/v1"
      : undefined,
    defaultHeaders: useOpenRouter
      ? {
          "HTTP-Referer": process.env.OPENROUTER_HTTP_REFERER || "http://localhost:3000",
          "X-Title": process.env.OPENROUTER_APP_NAME || "ai-dev-server",
        }
      : undefined,
  });
}

export async function generateProject(request: GenerateRequest): Promise<GenerationResult> {
  const client = getClient();

  const response = await client.chat.completions.create({
    model:
      process.env.OPENROUTER_MODEL ||
      process.env.OPENAI_MODEL ||
      "openai/gpt-4o-mini",
    temperature: 0,
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: buildGenerationPrompt(request.prompt) },
    ],
  });

  const content = response.choices[0]?.message?.content ?? "";
  const cleaned = ensureNonEmpty(stripMarkdownFences(content));
  const parsed = parseGenerationResult(cleaned);

  return {
    outputDir: runtimeConfig.outputDir,
    files: normalizeFiles(parsed.files),
    summary: parsed.summary,
  };
}

export async function refineProject(request: GenerateRequest): Promise<GenerationResult> {
  const client = getClient();
  const snapshot = snapshotProject(runtimeConfig.outputDir, 12)
    .map((entry) => `--- FILE: ${entry.path} ---\n${entry.content}\n`)
    .join("\n");

  const response = await client.chat.completions.create({
    model:
      process.env.OPENROUTER_MODEL ||
      process.env.OPENAI_MODEL ||
      "openai/gpt-4o-mini",
    temperature: 0,
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: buildRefinePrompt(request.prompt, snapshot) },
    ],
  });

  const content = response.choices[0]?.message?.content ?? "";
  const cleaned = ensureNonEmpty(stripMarkdownFences(content));
  const parsed = parseGenerationResult(cleaned);

  return {
    outputDir: runtimeConfig.outputDir,
    files: normalizeFiles(parsed.files),
    summary: parsed.summary,
  };
}

export function writeGeneratedProject(result: GenerationResult) {
  removeDir(result.outputDir);
  ensureDir(result.outputDir);

  for (const file of result.files) {
    const targetPath = path.join(result.outputDir, file.path);
    ensureDir(path.dirname(targetPath));
    writeTextFile(targetPath, normalizeServerContent(file.path, file.content));
  }
}

export function installGeneratedProject(result: GenerationResult) {
  const packageJsonPath = path.join(result.outputDir, "package.json");
  if (!fs.existsSync(packageJsonPath)) {
    throw new Error("Generated project is missing package.json");
  }

  const installResult = runCommand("npm", ["install"], result.outputDir);
  if (installResult.status !== 0) {
    throw new Error("npm install failed in generated project");
  }

  return result;
}
