import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

export interface SnapshotFile {
  path: string;
  content: string;
}

export function ensureDir(dirPath: string) {
  fs.mkdirSync(dirPath, { recursive: true });
}

export function writeTextFile(filePath: string, content: string) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf8");
}

export function pathExists(filePath: string) {
  return fs.existsSync(filePath);
}

export function readTextFile(filePath: string) {
  return fs.readFileSync(filePath, "utf8");
}

export function listFilesRecursively(rootDir: string, maxFiles = 20) {
  const results: string[] = [];

  const walk = (dir: string) => {
    if (results.length >= maxFiles) {
      return;
    }

    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (results.length >= maxFiles) {
        return;
      }

      if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "dist") {
        continue;
      }

      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }

      if (entry.isFile()) {
        results.push(fullPath);
      }
    }
  };

  if (fs.existsSync(rootDir)) {
    walk(rootDir);
  }

  return results.sort();
}

export function snapshotProject(rootDir: string, maxFiles = 20): SnapshotFile[] {
  return listFilesRecursively(rootDir, maxFiles)
    .map((filePath) => ({
      path: path.relative(rootDir, filePath).replace(/\\/g, "/"),
      content: fs.readFileSync(filePath, "utf8"),
    }))
    .sort((left, right) => left.path.localeCompare(right.path));
}

export function removeDir(dirPath: string) {
  fs.rmSync(dirPath, { recursive: true, force: true });
}

export function runCommand(command: string, args: string[], cwd: string) {
  return spawnSync(command, args, {
    cwd,
    stdio: "inherit",
    shell: process.platform === "win32",
  });
}
