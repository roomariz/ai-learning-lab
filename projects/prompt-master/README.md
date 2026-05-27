# Prompt Master

A skill that writes optimized prompts for any AI tool. Zero tokens or credits wasted. Full context and memory retention. No re-prompting your way to an answer you should have gotten on attempt one.

**Works with:** Claude, ChatGPT, Gemini, o1/o3, MiniMax, Cursor, Claude Code, GitHub Copilot, Windsurf, Bolt, v0, Lovable, Devin, Perplexity, Midjourney, DALL-E, Stable Diffusion, ComfyUI, Sora, Runway, ElevenLabs, Zapier, Make, and any AI tool you throw at it.

---

## 🚀 Quick Start

### Web Interface

Run locally:
```bash
npm run dev
```
Then open http://localhost:3000

Or simply open `index.html` directly in your browser for a visual interface to:
- Generate optimized prompts for any AI tool
- Update/fix existing prompts
- Save prompts to a local library

### Claude Code / Claude.ai

Upload this skill via Claude's sidebar or use directly:

```
Write me a prompt for Cursor to refactor my auth module
```

```
I need a prompt for Claude Code to build a REST API
```

```
Generate a Midjourney prompt for a cyberpunk city at night
```

---

## 🎯 Usage Examples

### Generate a Prompt

```
/prompt-master

I want a prompt for Claude Code to build a todo app with React and Supabase
```

### Fix an Existing Prompt

```
Here's a bad prompt I wrote for GPT-4o, fix it: [paste prompt]
```

### Adapt for Different Tools

```
Break this prompt down and adapt it for Stable Diffusion
```

---

## Key Features

- **Tool-specific optimization** — Each AI tool has unique prompting requirements. Prompt Master knows them all.
- **Token efficiency** — Every word is load-bearing. No padding, no wasted tokens.
- **Memory Block System** — Carries forward decisions from prior conversation turns.
- **35+ credit-killing patterns detected** — Automatically fixes vague tasks, missing constraints, wrong formats.
- **Safe techniques only** — Role assignment, few-shot, grounding anchors. Excludes hallucination-prone methods like Tree of Thought.

---

## Installation

### Claude.ai (browser)

1. Go to **Claude.ai → Sidebar → Customize → Skills → Upload a Skill**
2. Upload the `SKILL.md` file

### Claude Code

Clone to skills directory:
```bash
mkdir -p ~/.claude/skills
cp -r prompt-master ~/.claude/skills/
```

---

## License

MIT - See [LICENSE](LICENSE) for details.