#!/usr/bin/env node
import "dotenv/config";
import { Command } from "commander";
import chalk from "chalk";
import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import { generateProject, installGeneratedProject, refineProject, writeGeneratedProject } from "./generate.js";
import { renderDashboard } from "./dashboard.js";
import { runtimeConfig, setOutputDir, setRuntimePrompt } from "./runtime.js";
import { ensureDir, pathExists, writeTextFile } from "./utils/files.js";
import { createWatcher } from "./watcher.js";

let serverProcess: ChildProcess | null = null;
let watcher: ReturnType<typeof createWatcher> | null = null;
let shouldExitOnChildExit = true;

function findFreePort(preferredPort: number) {
  return new Promise<number>((resolve) => {
    const probe = (port: number) => {
      const server = net.createServer();

      server.unref();
      server.once("error", () => {
        server.close();
        if (port === 0) {
          resolve(preferredPort);
          return;
        }
        probe(0);
      });
      server.listen(port, () => {
        const address = server.address();
        server.close(() => {
          if (address && typeof address === "object") {
            resolve(address.port);
            return;
          }

          resolve(port);
        });
      });
    };

    probe(preferredPort);
  });
}

function stopServer() {
  if (serverProcess && !serverProcess.killed) {
    serverProcess.kill("SIGINT");
  }
  serverProcess = null;
}

async function startGeneratedServer(appDir: string, options: { exitOnChildExit?: boolean } = {}) {
  const startScript = path.join(appDir, "package.json");

  if (!pathExists(startScript)) {
    throw new Error(`No generated app found in ${appDir}. Run generate first.`);
  }

  if (!pathExists(path.join(appDir, "node_modules"))) {
    console.log(chalk.yellow("Dependencies not found. Installing..."));
    const installProcess = spawn("npm", ["install"], {
      cwd: appDir,
      stdio: "inherit",
      shell: process.platform === "win32",
    });

    const exitCode = await new Promise<number>((resolve, reject) => {
      installProcess.on("error", reject);
      installProcess.on("exit", (code) => resolve(code ?? 0));
    });

    if (exitCode !== 0) {
      throw new Error("npm install failed in generated project");
    }

    console.log(chalk.green("Dependencies installed successfully."));
  }

  const port = await findFreePort(Number(process.env.PORT || 3000));
  renderDashboard("running", `Starting app in ${appDir} on port ${port}...`);
  shouldExitOnChildExit = options.exitOnChildExit !== false;

  const child = spawn("npm", ["start"], {
    cwd: appDir,
    env: {
      ...process.env,
      PORT: String(port),
    },
    stdio: ["inherit", "pipe", "pipe"],
    shell: process.platform === "win32",
  });
  serverProcess = child;

  child.stdout?.on("data", (chunk: Buffer) => {
    process.stdout.write(chunk);
  });

  child.stderr?.on("data", (chunk: Buffer) => {
    process.stderr.write(chunk);
  });

  child.on("exit", (code) => {
    console.log(chalk.gray(`\nServer exited with code ${code ?? 0}`));
    if (shouldExitOnChildExit) {
      process.exit(code ?? 0);
    }
  });
}

const program = new Command();

program
  .name("ai-dev-server")
  .usage("[command] [options]")
  .description("Generate and run AI-assisted Express backends")
  .version("0.1.0")
  .showHelpAfterError("(run with --help for usage)")
  .addHelpText(
    "afterAll",
    `
Examples:
  npm run dev -- init
  npm run dev -- generate "build a simple express API with a health route"
  npm run dev -- run
  npm run dev -- watch
  npm run dev -- refine "add validation and improve the error responses"

OpenRouter:
  Set OPENROUTER_API_KEY to enable OpenRouter automatically.
  Optional: OPENROUTER_MODEL, OPENROUTER_HTTP_REFERER, OPENROUTER_APP_NAME
    `,
  );

program
  .command("init")
  .description("Create a new project scaffold")
  .action(() => {
    ensureDir(runtimeConfig.outputDir);

    if (!fs.existsSync(".env")) {
      writeTextFile(
        ".env",
        [
          "OPENROUTER_API_KEY=",
          "OPENROUTER_MODEL=openai/gpt-4o-mini",
          "OPENROUTER_HTTP_REFERER=http://localhost:3000",
          "OPENROUTER_APP_NAME=ai-dev-server",
          "",
        ].join("\n"),
      );
    }

    if (!fs.existsSync("ai-dev-server.config.json")) {
      writeTextFile(
        "ai-dev-server.config.json",
        JSON.stringify(
          {
            outputDir: "generated",
            provider: "openrouter",
            model: "openai/gpt-4o-mini",
          },
          null,
          2,
        ),
      );
    }

    renderDashboard("ready", "Scaffold ready.");
    console.log(chalk.green(`Created ${runtimeConfig.outputDir}`));
    console.log(chalk.gray("Created .env and ai-dev-server.config.json if they did not exist."));
    console.log(chalk.gray('Run: npm run dev -- generate "build a simple express API with a health route"'));
  });

program
  .command("generate")
  .argument("<prompt>", "generation prompt")
  .option("-o, --output <dir>", "output directory", runtimeConfig.outputDir)
  .description("Generate a backend project from a prompt")
  .action(async (prompt: string, options: { output?: string }) => {
    try {
      setRuntimePrompt(prompt);
      setOutputDir(options.output || runtimeConfig.outputDir);
      renderDashboard("running", "Generating project files...");
      const result = await generateProject({
        prompt,
        template: runtimeConfig.template,
      });
      writeGeneratedProject(result);
      installGeneratedProject(result);
      console.log(chalk.green(result.summary));
      console.log(chalk.gray(`Generated ${result.files.length} file(s) in ${result.outputDir}.`));
      console.log(chalk.cyan(`Next: cd ${path.relative(process.cwd(), result.outputDir) || "."} && npm start`));
    } catch (error) {
      console.error(chalk.red(error instanceof Error ? error.message : "Failed to generate project"));
      process.exitCode = 1;
    }
  });

program
  .command("refine")
  .argument("<prompt>", "refinement prompt")
  .option("-o, --output <dir>", "output directory", runtimeConfig.outputDir)
  .description("Refine the current generated project using the existing files as context")
  .action(async (prompt: string, options: { output?: string }) => {
    try {
      setRuntimePrompt(prompt);
      setOutputDir(options.output || runtimeConfig.outputDir);
      const startScript = path.join(runtimeConfig.outputDir, "package.json");

      if (!pathExists(startScript)) {
        throw new Error(`No generated app found in ${runtimeConfig.outputDir}. Run generate first.`);
      }

      renderDashboard("running", "Refining existing project...");
      const result = await refineProject({
        prompt,
        template: runtimeConfig.template,
      });
      writeGeneratedProject(result);
      installGeneratedProject(result);
      console.log(chalk.green(result.summary));
      console.log(chalk.gray(`Refined ${result.files.length} file(s) in ${result.outputDir}.`));
      console.log(chalk.cyan(`Next: cd ${path.relative(process.cwd(), result.outputDir) || "."} && npm start`));
    } catch (error) {
      console.error(chalk.red(error instanceof Error ? error.message : "Failed to refine project"));
      process.exitCode = 1;
    }
  });

program
  .command("run")
  .option("-o, --output <dir>", "output directory", runtimeConfig.outputDir)
  .description("Run the generated project")
  .action(async (options: { output?: string }) => {
    setOutputDir(options.output || runtimeConfig.outputDir);
    const appDir = runtimeConfig.outputDir;
    try {
      await startGeneratedServer(appDir);
    } catch (error) {
      console.error(chalk.red(error instanceof Error ? error.message : "Failed to start server"));
      process.exitCode = 1;
      return;
    }

    process.once("SIGINT", () => {
      stopServer();
      process.exit(0);
    });
  });

program
  .command("watch")
  .option("-o, --output <dir>", "output directory", runtimeConfig.outputDir)
  .description("Watch generated files and restart on changes")
  .action(async (options: { output?: string }) => {
    setOutputDir(options.output || runtimeConfig.outputDir);
    const appDir = runtimeConfig.outputDir;

    try {
      await startGeneratedServer(appDir, { exitOnChildExit: false });
    } catch (error) {
      console.error(chalk.red(error instanceof Error ? error.message : "Failed to start server"));
      process.exitCode = 1;
      return;
    }

    watcher = createWatcher(appDir, async () => {
      if (!serverProcess) {
        return;
      }

      renderDashboard("restarting", "File change detected. Restarting...");
      stopServer();
      try {
        await startGeneratedServer(appDir, { exitOnChildExit: false });
      } catch (error) {
        console.error(chalk.red(error instanceof Error ? error.message : "Failed to restart server"));
      }
    });

    process.once("SIGINT", () => {
      if (watcher) {
        watcher.close();
      }
      stopServer();
      process.exit(0);
    });
  });

program.parseAsync(process.argv);
