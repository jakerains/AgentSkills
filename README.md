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

Works with **18+ AI coding agents** via [skills.sh](https://skills.sh):

| Agent | Agent | Agent |
|-------|-------|-------|
| AMP | Antigravity | Claude Code |
| ClawdBot | Cline | Codex |
| Cursor | Droid | Gemini |
| GitHub Copilot | Goose | Kilo |
| Kiro CLI | OpenCode | Roo |
| Trae | VSCode | Windsurf |

---

## Available Skills

### codex-app-server
> Embed Codex into rich apps with the Codex App Server

**Use for:** Building Electron, Swift, Next.js, and Node/TypeScript Codex clients, integrating Codex into existing apps, ChatGPT or API-key login flows, external ChatGPT token refresh, streamed thread/turn/item events, approvals, and version-matched App Server schema generation

```bash
npx skills add jakerains/AgentSkills --skill codex-app-server
```

---

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

### onnx-webgpu-converter
> Convert HuggingFace models to ONNX for browser inference with Transformers.js + WebGPU

**Use for:** ONNX conversion, optimum-cli export, model quantization (fp16/q8/q4), Transformers.js setup, WebGPU inference, running ML models in the browser

```bash
npx skills add jakerains/AgentSkills --skill onnx-webgpu-converter
```

---

### apple-foundation-models
> Build Apple Intelligence features with Foundation Models and Image Playground on iOS 26+, macOS 26+, and visionOS 26+

**Use for:** SystemLanguageModel, LanguageModelSession, streaming responses, guided generation with @Generable, tool calling, prompt design, safety and guardrails, model capabilities and limitations, custom adapters, local vs larger-model routing, and ImagePlayground/ImageCreator integration

```bash
npx skills add jakerains/AgentSkills --skill apple-foundation-models
```

---

### macos-dmg-builder
> Build, sign, notarize, and package native macOS apps into distributable DMGs

**Use for:** SwiftUI/AppKit/Xcode release pipelines, Developer ID code signing, notarytool credential setup, DMG creation and notarization, debugging codesign/notarization failures

```bash
npx skills add jakerains/AgentSkills --skill macos-dmg-builder
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
