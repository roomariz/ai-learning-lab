import { spawn, type ChildProcess } from "node:child_process";

export function startNodeProcess(filePath: string): ChildProcess {
  return spawn(process.execPath, [filePath], {
    stdio: ["ignore", "pipe", "pipe"],
  });
}

export function stopProcess(child: ChildProcess | null) {
  if (child && !child.killed) {
    child.kill("SIGINT");
  }
}
