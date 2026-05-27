# Vercel Project Configuration

## `ai-learning-lab-portal`

- Root directory: `apps/portal`
- Framework preset: Next.js
- Build command: `npm run build`
- Output directory: `.next`
- Install command: `npm install`
- Environment variables: none initially
- Domain: `ai-learning-lab.roomariz.dev`

## `prompt-master`

- Root directory: `projects/prompt-master`
- Framework preset: Other / Static
- Build command: none
- Output directory: `.`
- Install command: optional, not required for static hosting
- Environment variables: none
- Domain: `prompt-master.roomariz.dev`

## `hf-model-scanner-report`

- Root directory: repository root
- Framework preset: Other / Static
- Build command: `bash projects/11-hf-provider-model-scanner/build_vercel.sh`
- Output directory: `projects/11-hf-provider-model-scanner/.vercel-output-static`
- Install command: none
- Environment variables: none for static deployment
- Domain: `hf-scanner.roomariz.dev`

Do not set `HF_TOKEN` in this Vercel project. The deployed artifact is static and must not run provider probes.
