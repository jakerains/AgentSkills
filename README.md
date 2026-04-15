# Jake's Agent Skills

**A personal collection of skills I built because I couldn't find them anywhere else.**

I kept running into the same problem: I'd need my AI agent to do something specific — convert a model to ONNX for the browser, generate a shot list from a screenplay, build a macOS DMG — and there just wasn't a skill for it. So I started making my own.

Some of these are broadly useful and you'll probably get a lot of mileage out of them. Others are pretty niche or tailored to my own workflows. Either way, they're all here if you want them.

---

## Quick Start

```bash
# Install all skills
npx skills add jakerains/AgentSkills

# Or just grab one
npx skills add jakerains/AgentSkills --skill <skill-name>
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

> Skills I use all the time are marked with a star. The rest are still solid — just more situational or specific to stuff I work on.

### elevenlabs-maxx ★
> The full ElevenLabs platform — TTS, STT, voice cloning, sound effects, music, dialogue, agents, dubbing, and every API endpoint

I use ElevenLabs constantly and the docs are sprawling. This skill covers all three interfaces — MCP (24 tools), Agents CLI, and the full API for stuff MCP can't do (text-to-dialogue, forced alignment, Studio projects, pronunciation dictionaries, history management, batch calling, and more).

**Use for:** Text-to-speech, speech-to-text, voice cloning, sound effects, music, multi-speaker dialogue, dubbing, voice agents, MCP setup, API integration

```bash
npx skills add jakerains/AgentSkills --skill elevenlabs-maxx
```

---

### elevenlabs-agent-builder
> Build, validate, and deploy ElevenLabs Conversational AI voice agents end-to-end

Focused companion to `elevenlabs-maxx` for voice agents specifically. Ships a schema-aware validator, a deploy-with-tools script, knowledge base upload, and migration cheatsheets for Retell, Vapi, and Bland — so you can port an existing voice bot or build one from a call script in a single pass.

**Use for:** Building voice agents, phone bots, IVR flows, migrating from Retell/Vapi/Bland, validating agent JSON, knowledge base prep, fixing agent deployment errors

```bash
npx skills add jakerains/AgentSkills --skill elevenlabs-agent-builder
```

---

### skill-seekers ★
> Turn any documentation into an installable agent skill

If you find yourself wishing a skill existed for some library or tool, this skill helps you make one from the docs. Probably the most meta thing in here.

**Use for:** Converting docs sites, GitHub repos, and PDFs into skills

```bash
npx skills add jakerains/AgentSkills --skill skill-seekers
```

---

### docxmakebetter ★
> Create, edit, and analyze Word documents with tracked changes, comments, and redlining

Surprisingly hard to get AI agents to work with .docx files properly. This one handles it.

**Use for:** Creating .docx files, tracked changes, comments, redlining workflows, document review, text extraction

```bash
npx skills add jakerains/AgentSkills --skill docxmakebetter
```

---

### nextjs-pwa ★
> Build Progressive Web Apps with Next.js

PWA setup with Next.js has a lot of gotchas. This skill covers service workers, offline support, caching, push notifications, and install prompts without the agent guessing wrong.

**Use for:** PWA setup, Serwist/next-pwa config, service workers, offline support, caching strategies

```bash
npx skills add jakerains/AgentSkills --skill nextjs-pwa
```

---

### update-changelog ★
> Automated changelog management and version bumping

I got tired of manually maintaining changelogs. This skill handles the whole flow — changelog entries, version bumps, semantic versioning, even UI components for displaying the version.

**Use for:** Changelogs, version bumping, release tracking, semantic versioning

```bash
npx skills add jakerains/AgentSkills --skill update-changelog
```

---

### onnx-webgpu-converter
> Convert HuggingFace models to ONNX for browser inference with Transformers.js + WebGPU

This is pretty niche but if you're doing on-device ML in the browser, it's a lifesaver. Covers the full pipeline from HuggingFace model to quantized ONNX running in WebGPU.

**Use for:** ONNX conversion, optimum-cli export, model quantization (fp16/q8/q4), Transformers.js, WebGPU inference

```bash
npx skills add jakerains/AgentSkills --skill onnx-webgpu-converter
```

---

### apple-foundation-models
> Build Apple Intelligence features with Foundation Models on iOS 26+, macOS 26+, and visionOS 26+

This one is very new — Apple's on-device models are bleeding edge and the docs are still sparse. I built this so the agent actually knows the API surface instead of hallucinating Swift code.

**Use for:** SystemLanguageModel, streaming, guided generation with @Generable, tool calling, safety/guardrails, ImagePlayground

```bash
npx skills add jakerains/AgentSkills --skill apple-foundation-models
```

---

### macos-dmg-builder
> Build, sign, notarize, and package macOS apps into distributable DMGs

The macOS code signing and notarization pipeline is genuinely painful. This skill walks through the whole process so the agent doesn't skip steps or get the order wrong.

**Use for:** SwiftUI/AppKit release pipelines, Developer ID signing, notarytool, DMG creation, debugging codesign failures

```bash
npx skills add jakerains/AgentSkills --skill macos-dmg-builder
```

---

### vercel-workflow
> Build durable, long-running workflows with Vercel's Workflow DevKit

Useful if you're building background jobs, AI agent pipelines, or anything that needs retry logic and multi-step flows on Vercel.

**Use for:** Background jobs, AI agents, webhooks, scheduled tasks, retry logic, multi-step workflows

```bash
npx skills add jakerains/AgentSkills --skill vercel-workflow
```

---

### codex-app-server
> Embed Codex into rich apps with the Codex App Server

Pretty specific to building apps that integrate OpenAI's Codex. If that's your thing, this covers Electron, Swift, Next.js clients, auth flows, and streaming events.

**Use for:** Codex client integration, ChatGPT/API-key login, streamed events, approvals

```bash
npx skills add jakerains/AgentSkills --skill codex-app-server
```

---

### shot-list
> Generate professional shot lists from screenplays

This one is definitely a "Jake skill." I do video production work and needed a way to break down scripts into shot lists. If you're in film/video, it's great. Otherwise, probably not your thing.

**Use for:** Film/video production planning, screenplay breakdowns, shot planning

```bash
npx skills add jakerains/AgentSkills --skill shot-list
```

---

### nextstep-tours
> Product tours and onboarding with NextStep v2 for Next.js

Built this for a specific project. If you're using NextStep for guided tours and onboarding flows, this is exactly what you need. Otherwise you probably won't reach for it.

**Use for:** Guided tours, onboarding flows, feature walkthroughs, interactive tutorials

```bash
npx skills add jakerains/AgentSkills --skill nextstep-tours
```

---

### sam3
> Meta SAM 3 for open-vocabulary image and video segmentation

Another niche one. If you're working with Meta's Segment Anything Model 3, this covers setup, checkpoint auth, segmentation workflows, and fine-tuning. Built it when I was experimenting with SAM3 and the agent kept getting the setup wrong.

**Use for:** SAM3 setup, HuggingFace checkpoint auth, image/video segmentation, fine-tuning

```bash
npx skills add jakerains/AgentSkills --skill sam3
```

---

## Installation Options

```bash
# Install all skills
npx skills add jakerains/AgentSkills

# Install a specific skill
npx skills add jakerains/AgentSkills --skill <skill-name>

# Install globally (available in all projects)
npx skills add jakerains/AgentSkills --skill <skill-name> -g

# List what's available
npx skills add jakerains/AgentSkills --list
```

---

## What Are Skills?

If you're new to this — skills are modular packages that give AI coding agents specialized knowledge they don't have out of the box. They can include domain expertise, step-by-step workflows, executable scripts, and best practices for specific tools or technologies.

Once installed, your agent automatically loads the relevant skill based on what you're doing. You don't have to think about it.

---

## Making Your Own

If you want to build skills like these, each one is just a folder with a `SKILL.md` file:

```
skills/your-skill/
├── SKILL.md              # Main skill file with YAML frontmatter
└── references/           # Optional: detailed docs loaded on-demand
```

See [CLAUDE.md](CLAUDE.md) for the full creation guide, or use the `skill-seekers` skill to generate one from existing docs.

---

## License

MIT

---

<p align="center">
  <a href="https://add-skill.org">Powered by add-skill</a>
</p>
