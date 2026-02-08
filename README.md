# Agent Skills

**Supercharge your AI coding agent with powerful skills.**

Skills are modular packages that give AI agents specialized knowledge, workflows, and capabilities. Install them once, use them everywhere.

---

## Quick Start

```bash
# Install all skills (works instantly via npx)
npx skills add jakerains/AgentSkills
```

## Supported Agents

| Agent | Project Location | Global Location |
|-------|------------------|-----------------|
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` |
| **OpenCode** | `.opencode/skill/` | `~/.config/opencode/skill/` |
| **Codex** | `.codex/skills/` | `~/.codex/skills/` |
| **Cursor** | `.cursor/skills/` | `~/.cursor/skills/` |

---

## Available Skills

### vercel-workflow
> Build durable, long-running workflows with Vercel's Workflow DevKit

**Use for:** Background jobs, AI agents, webhooks, scheduled tasks, retry logic, multi-step workflows in Next.js

```bash
npx skills add jakerains/AgentSkills --skill vercel-workflow
```

---

### elevenlabs
> Complete ElevenLabs AI audio platform

**Use for:** Text-to-speech, speech-to-text, voice cloning, sound effects, music generation, dubbing, voice agents, voice changer, and all ElevenLabs API/SDK/MCP features

```bash
npx skills add jakerains/AgentSkills --skill elevenlabs
```

---

### skill-seekers
> Convert any documentation into an agent skill

**Use for:** Turning docs websites, GitHub repos, and PDFs into installable skills

```bash
npx skills add jakerains/AgentSkills --skill skill-seekers
```

---

### shot-list
> Generate professional shot lists from scripts

**Use for:** Film/video production planning, screenplay breakdowns, shot planning

```bash
npx skills add jakerains/AgentSkills --skill shot-list
```

---

### nextjs-pwa
> Build Progressive Web Apps with Next.js

**Use for:** PWA setup, service workers, offline support, caching strategies, push notifications, install prompts, Serwist/next-pwa configuration

```bash
npx skills add jakerains/AgentSkills --skill nextjs-pwa
```

---

### sam3
> Create and work with Meta SAM 3 for open-vocabulary segmentation

**Use for:** SAM3 setup, Hugging Face checkpoint auth, image/video segmentation workflows, Python integration, fine-tuning, and SA-Co evaluation

```bash
npx skills add jakerains/AgentSkills --skill sam3
```

---

### docxmakebetter
> Comprehensive Word document creation, editing, and analysis

**Use for:** Creating .docx files, tracked changes, comments, redlining workflows, document review, text extraction from Word documents

```bash
npx skills add jakerains/AgentSkills --skill docxmakebetter
```

---

## Installation Options

```bash
# List all available skills
npx skills add jakerains/AgentSkills --list

# Install a specific skill to current project
npx skills add jakerains/AgentSkills --skill <skill-name>

# Install globally (available in all projects)
npx skills add jakerains/AgentSkills --skill <skill-name> -g

# Install all skills at once
npx skills add jakerains/AgentSkills

# Non-interactive mode (for CI/CD)
npx skills add jakerains/AgentSkills --skill <skill-name> -y
```

---

## What Are Skills?

Skills extend AI coding agents with:

- **Specialized Knowledge** — Domain expertise the agent can reference
- **Workflows** — Step-by-step processes for complex tasks
- **Tools & Scripts** — Executable code for deterministic operations
- **Best Practices** — Patterns and conventions for specific technologies

Once installed, your agent automatically loads relevant skills based on context.

---

## Contributing

Have a skill idea? PRs welcome! Each skill needs:

```
skills/your-skill/
├── SKILL.md              # Main skill file with YAML frontmatter
└── references/           # Optional: detailed docs loaded on-demand
```

See [CLAUDE.md](CLAUDE.md) for the full skill creation guide.

---

## License

MIT

---

<p align="center">
  <a href="https://add-skill.org">Powered by add-skill</a>
</p>
