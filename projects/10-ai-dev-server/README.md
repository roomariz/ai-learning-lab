# ai-dev-server

CLI tool that generates, validates, runs, and hot-reloads Express.js backends from natural language prompts.

## Quick Start

```bash
npm install
```

Create a `.env` file with your OpenRouter key:

```bash
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_HTTP_REFERER=http://localhost:3000
OPENROUTER_APP_NAME=ai-dev-server
```

Then run:

```bash
npm run dev -- init
npm run dev -- generate "build a simple express API with a health route"
npm run dev -- run
```

## What it does

- scaffolds a backend project from a prompt
- generates files with OpenRouter or OpenAI
- validates the generated structure before writing files
- refines an existing generated project using the current files as context
- installs dependencies
- runs the generated server
- watches files and restarts on change

## Usage

```bash
npm run dev -- init
npm run dev -- generate "build a simple express API with a health route"
npm run dev -- refine "add better validation and clearer error responses"
npm run dev -- run
npm run dev -- watch
```

End-to-end example:

```bash
npm run dev -- generate "build a simple express API with a health route"
```

Expected output:
```text
Generated backend files.
Generated 4 file(s) in generated.
```

Resulting structure:
```txt
generated/
  package.json
  src/
    server.js
    app.js
    routes/
      health.js
```

Failure example:

```bash
npm run dev -- generate "<<< malformed output >>>"
```

Expected result:
```text
parser validation error
```

Global install:

```bash
npm link
ai-dev-server generate "build a simple express API with a health route"
```

Help:

```bash
npm run dev -- --help
```

Version:

```bash
npm run dev -- --version
```

## Project structure

```txt
src/
  cli.ts
  generate.ts
  runtime.ts
  watcher.ts
  dashboard.ts
  prompts.ts
  types.ts
  utils/
    files.ts
    process.ts
    clean-output.ts
templates/
  express-basic/
```

## Status

This repository now has a working CLI MVP: init, generate, refine, run, and watch.

## Why This Stands Out

`ai-dev-server` is not just an AI code generator. It is a local CLI workflow that turns a prompt into a runnable backend scaffold, installs dependencies, starts the server, and supports refinement with the existing codebase as context.

What it demonstrates:
- strict output validation instead of free-form model text
- fail-fast behavior when the generated structure is invalid
- multi-file project generation with safe file writes
- local process control, port fallback, and watch/restart behavior
- iterative refinement rather than one-shot generation

Why that matters:
- recruiters can see product thinking, not just API calls
- the tool solves a real developer workflow: generate -> install -> run -> refine
- the code shows architecture, safety, and developer-experience concerns
- the strict parser and tests prove the AI is treated as one component in a controlled system

Typical flow:

```bash
npm run dev -- init
npm run dev -- generate "build a simple express API with a health route"
npm run dev -- refine "add validation and cleaner error responses"
npm run dev -- run
```

## OpenRouter

To use OpenRouter instead of a direct OpenAI key, set:

```bash
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_HTTP_REFERER=http://localhost:3000
OPENROUTER_APP_NAME=ai-dev-server
```

The app will automatically use OpenRouter when `OPENROUTER_API_KEY` is present.

If `generated/node_modules` is missing, `run` installs dependencies automatically before starting the server.

## Testing

Run the parser and snapshot tests with:

```bash
npm run test
```

The suite focuses on the strict generation contract:
- valid payloads pass
- missing required files fail
- invalid `package.json` rules fail
- path traversal fails
- non-JSON output fails
- refine snapshots preserve exact file paths and contents

## Notes

- `generated/` is ignored in git so the repo stays focused on the tool, not its output
- `npm run dev -- --help` shows the CLI usage and command examples
