export type ProjectTemplate = "express-basic";

export interface GenerateRequest {
  prompt: string;
  template: ProjectTemplate;
}

export interface GeneratedFile {
  path: string;
  content: string;
}

export interface GenerationResult {
  outputDir: string;
  files: GeneratedFile[];
  summary: string;
}

export interface RuntimeState {
  status: "idle" | "running" | "restarting" | "stopped" | "error";
  filePath?: string;
  message?: string;
}
