# Agent Skills Collection

A library of skills for AI coding agents.

## Supported Agents

Works with **Claude Code**, **OpenCode**, **Codex**, and **Cursor**.

## Installation

```bash
# List available skills
npx add-skill jakerains/claudeskills --list

# Install a specific skill
npx add-skill jakerains/claudeskills --skill elevenlabs-voice-agents
npx add-skill jakerains/claudeskills --skill skill-seekers
npx add-skill jakerains/claudeskills --skill shot-list
npx add-skill jakerains/claudeskills --skill vercel-workflow

# Install all skills
npx add-skill jakerains/claudeskills

# Install globally (available in all projects)
npx add-skill jakerains/claudeskills --skill vercel-workflow -g
```

## Skills

| Skill | Description |
|-------|-------------|
| [elevenlabs-voice-agents](skills/elevenlabs-voice-agents/) | Create and deploy ElevenLabs conversational voice agents, phone bots, and voice assistants |
| [skill-seekers](skills/skill-seekers/) | Convert documentation websites, GitHub repos, and PDFs into Claude skills |
| [shot-list](skills/shot-list/) | Generate professional shot lists from screenplays and scripts |
| [vercel-workflow](skills/vercel-workflow/) | Build durable workflows with Vercel Workflow DevKit - long-running tasks, AI agents, webhooks, retries in Next.js |

## License

MIT
