import chalk from "chalk";
import { runtimeConfig } from "./runtime.js";

export function renderDashboard(status: string, message = "") {
  console.clear();
  console.log(chalk.bold.blue("=== AI DEV SERVER ===\n"));
  console.log(`${chalk.white("Status: ")}${chalk.green(status)}`);
  console.log(`${chalk.white("Project: ")}${chalk.gray(runtimeConfig.outputDir)}`);
  console.log(`${chalk.white("Prompt: ")}${chalk.gray(runtimeConfig.prompt || "n/a")}`);
  if (message) {
    console.log(`${chalk.white("Message: ")}${chalk.gray(message)}`);
  }
  console.log("");
  console.log(chalk.gray("Commands: init | generate | refine | run | watch"));
}
