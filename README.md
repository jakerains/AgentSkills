# Jake's Agent Skills

**My personal collection of custom agent skills.**

Skills I've built for my own projects and workflows, gathered here in one place. Some are broadly useful, others are shaped around how I like to work. Install the whole set or just grab the ones you want.

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

> Each entry includes the date I last updated that skill.

Click a skill to jump to its details below (each section has a one-click-copy install block), or grab the command straight from here:

| Skill | What it does | Install |
|-------|--------------|---------|
| [claude-advisor](#claude-advisor) | Consult Claude Fable as a read-only second-opinion advisor | `npx skills add jakerains/AgentSkills --skill claude-advisor` |
| [prompt-scheduler](#prompt-scheduler) | Schedule local Claude/Codex terminal prompts in Warp via launchd | `npx skills add jakerains/AgentSkills --skill prompt-scheduler` |
| [plaud](#plaud) | Search, transcribe & summarize Plaud voice recordings (CLI + MCP) | `npx skills add jakerains/AgentSkills --skill plaud` |
| [simplify](#simplify) | Clean up changed code — portable clone of Claude Code's /simplify | `npx skills add jakerains/AgentSkills --skill simplify` |
| [skill-seekers](#skill-seekers) | Turn any documentation into an installable skill | `npx skills add jakerains/AgentSkills --skill skill-seekers` |
| [kain-personality](#kain-personality) | The Kain Jares / GenAIAlien persona for writing & image prompts | `npx skills add jakerains/AgentSkills --skill kain-personality` |
| [jake-speak](#jake-speak) | Explain technical work in plain-English boxed cards | `npx skills add jakerains/AgentSkills --skill jake-speak` |
| [docxmakebetter](#docxmakebetter) | Create/edit Word docs — tracked changes, comments, redlining | `npx skills add jakerains/AgentSkills --skill docxmakebetter` |
| [nextjs-pwa](#nextjs-pwa) | Build Progressive Web Apps with Next.js | `npx skills add jakerains/AgentSkills --skill nextjs-pwa` |
| [update-changelog](#update-changelog) | Changelog management, version bumping & release publishing | `npx skills add jakerains/AgentSkills --skill update-changelog` |
| [onnx-webgpu-converter](#onnx-webgpu-converter) | Convert HuggingFace models to ONNX for the browser (Transformers.js + WebGPU) | `npx skills add jakerains/AgentSkills --skill onnx-webgpu-converter` |
| [apple-foundation-models](#apple-foundation-models) | Apple Intelligence / Foundation Models on iOS 26+, macOS 26+, visionOS 26+ | `npx skills add jakerains/AgentSkills --skill apple-foundation-models` |
| [macos-dmg-builder](#macos-dmg-builder) | Build, sign, notarize & package macOS apps into DMGs | `npx skills add jakerains/AgentSkills --skill macos-dmg-builder` |
| [vercel-workflow](#vercel-workflow) | Durable, long-running workflows with Vercel Workflow DevKit | `npx skills add jakerains/AgentSkills --skill vercel-workflow` |
| [codex-app-server](#codex-app-server) | Embed Codex into rich apps with the Codex App Server | `npx skills add jakerains/AgentSkills --skill codex-app-server` |
| [shot-list](#shot-list) | Generate professional shot lists from screenplays | `npx skills add jakerains/AgentSkills --skill shot-list` |
| [nextstep-tours](#nextstep-tours) | Product tours & onboarding with NextStep v2 for Next.js | `npx skills add jakerains/AgentSkills --skill nextstep-tours` |
| [driverjs-tours](#driverjs-tours) | Product tours, highlights & feature hints with Driver.js (any framework) | `npx skills add jakerains/AgentSkills --skill driverjs-tours` |
| [sam3](#sam3) | Meta SAM 3 open-vocabulary image & video segmentation | `npx skills add jakerains/AgentSkills --skill sam3` |
| [worktree-bootstrap](#worktree-bootstrap) | Make a new git worktree run its dev server like main | `npx skills add jakerains/AgentSkills --skill worktree-bootstrap` |

### claude-advisor
> Consult Claude Fable as an independent, read-only second-opinion advisor through the local Claude Code CLI

**Last updated:** 2026-07-12

Gives an agent a safe, one-shot way to get a second engineering opinion from **Claude Fable** when it judges that another perspective would genuinely help — a hard decision, a stubborn bug, a design or code review, a tradeoff call. A bundled wrapper (`consult-fable.sh`) runs `claude -p --model fable` in the active project, locked to read-only tools with all MCP servers stripped, so Fable can inspect files but can't edit anything or run commands. Each consultation is saved as a Markdown file under `docs/fable/` so you can read exactly what Fable said, and the agent can run it in the background while it keeps working. It's a **discretionary capability, not an always-on review**: the agent decides when to invoke it, verifies the advice, and still owns every decision and change.

**Use for:** Getting a second opinion before committing to an approach, pressure-testing ambiguous reasoning, design/architecture critique, code or plan review, debugging help, risk and tradeoff analysis

```bash
npx skills add jakerains/AgentSkills --skill claude-advisor
```

---

### prompt-scheduler
> Schedule local Claude, Codex, or agent terminal prompts to run later in Warp with launchd

**Last updated:** 2026-07-02

This captures the late-night usage-reset workflow: create a one-time local macOS schedule from the system clock, open the prompt in Warp via a `.command` file, keep the command pinned to the right working directory, tag the job for tracking, and leave logs plus launchctl verification behind.

**Use for:** Scheduling local Claude or Codex resume prompts, usage-reset restarts, Warp-visible one-time terminal jobs, launchd setup, prompt tags, delayed local agent commands

```bash
npx skills add jakerains/AgentSkills --skill prompt-scheduler
```

---

### plaud
> Install and use the Plaud CLI and MCP server to search, transcribe, and summarize voice recordings from any agent

**Last updated:** 2026-06-29

Plaud ships two surfaces — a terminal CLI (`@plaud-ai/cli`) and an MCP server (`@plaud-ai/mcp`) that auto-installs into Claude Code, Claude Desktop, Cursor, Windsurf, Codex, VS Code, Zed, plus an HTTP variant for Claude Web and ChatGPT. This skill picks the right one for the task, documents the install for both, and bundles a cookbook for shell pipelines and cross-surface workflows the MCP can't do on its own (bulk transcript export, scheduled digests, exit-code-aware re-auth).

**Use for:** Installing the Plaud CLI or MCP, choosing between them, searching recordings, reading transcripts and AI summaries, bulk-exporting transcripts, drafting follow-ups from a meeting, troubleshooting Plaud auth or MCP "server disconnected"

```bash
npx skills add jakerains/AgentSkills --skill plaud
```

---

### simplify
> Portable clone of Claude Code's `/simplify` — clean up changed code through four quality lenses

**Last updated:** 2026-07-06

Brings the `/simplify` cleanup workflow to agents that don't ship it (Codex, Cursor, etc.). Reviews your git diff through four lenses — **Reuse**, **Simplification**, **Efficiency**, **Altitude** — presents the findings, and applies the fixes on your approval. Quality only: it does not hunt for correctness bugs. **Do not install in Claude Code** — it has a superior native `/simplify` built for that harness.

**Use for:** Tidying up recent edits before a commit or PR, spotting duplicated logic, removing needless complexity, catching bandaid fixes that belong one layer deeper

```bash
npx skills add jakerains/AgentSkills --skill simplify
```

---

### skill-seekers
> Turn any documentation into an installable agent skill

**Last updated:** 2026-03-31

If you find yourself wishing a skill existed for some library or tool, this skill helps you make one from the docs. Probably the most meta thing in here.

**Use for:** Converting docs sites, GitHub repos, and PDFs into skills

```bash
npx skills add jakerains/AgentSkills --skill skill-seekers
```

---

### kain-personality
> Invoke the Kain Jares / GenAIAlien personality for writing, product reactions, parody concepts, and image prompts

**Last updated:** 2026-04-30

This is my reusable Kain mode: part public-builder voice, part GenAI alien mascot, part "how would Kain actually feel about this?" It includes the voice model, reference images, visual style rules, and a quick checker for short social drafts.

**Use for:** Kain-style posts, captions, replies, dialogue, character concepts, product reactions, parody scenarios, GenAIAlien image prompts

```bash
npx skills add jakerains/AgentSkills --skill kain-personality
```

---

### jake-speak
> Explain technical work to Jake in plain-English boxed cards, with optional standalone HTML recaps

**Last updated:** 2026-06-29

This is the personal "tell me what this means, not how the plumbing works" mode. It keeps the real product names, status, risks, and important numbers while stripping out code mechanics.

**Use for:** Jake Speak recaps, plain-English explanations, non-technical summaries of work just done, product or system explainers, optional Desktop HTML recap pages

```bash
npx skills add jakerains/AgentSkills --skill jake-speak
```

---

### docxmakebetter
> Create, edit, and analyze Word documents with tracked changes, comments, and redlining

**Last updated:** 2026-03-31

Surprisingly hard to get AI agents to work with .docx files properly. This one handles it.

**Use for:** Creating .docx files, tracked changes, comments, redlining workflows, document review, text extraction

```bash
npx skills add jakerains/AgentSkills --skill docxmakebetter
```

---

### nextjs-pwa
> Build Progressive Web Apps with Next.js

**Last updated:** 2026-02-01

PWA setup with Next.js has a lot of gotchas. This skill covers service workers, offline support, caching, push notifications, and install prompts without the agent guessing wrong.

**Use for:** PWA setup, Serwist/next-pwa config, service workers, offline support, caching strategies

```bash
npx skills add jakerains/AgentSkills --skill nextjs-pwa
```

---

### update-changelog
> Automated changelog management, version bumping, and release publishing

**Last updated:** 2026-06-29

I got tired of manually maintaining changelogs. This skill handles the whole flow — changelog entries, version bumps, semantic versioning, release tags, GitHub Releases, even UI components for displaying the version.

**Use for:** Changelogs, version bumping, release tracking, semantic versioning, tags, GitHub Releases

```bash
npx skills add jakerains/AgentSkills --skill update-changelog
```

---

### onnx-webgpu-converter
> Convert HuggingFace models to ONNX for browser inference with Transformers.js + WebGPU

**Last updated:** 2026-02-10

This is pretty niche but if you're doing on-device ML in the browser, it's a lifesaver. Covers the full pipeline from HuggingFace model to quantized ONNX running in WebGPU.

**Use for:** ONNX conversion, optimum-cli export, model quantization (fp16/q8/q4), Transformers.js, WebGPU inference

```bash
npx skills add jakerains/AgentSkills --skill onnx-webgpu-converter
```

---

### apple-foundation-models
> Build Apple Intelligence features with Foundation Models on iOS 26+, macOS 26+, and visionOS 26+

**Last updated:** 2026-03-17

This one is very new — Apple's on-device models are bleeding edge and the docs are still sparse. I built this so the agent actually knows the API surface instead of hallucinating Swift code.

**Use for:** SystemLanguageModel, streaming, guided generation with @Generable, tool calling, safety/guardrails, ImagePlayground

```bash
npx skills add jakerains/AgentSkills --skill apple-foundation-models
```

---

### macos-dmg-builder
> Build, sign, notarize, and package macOS apps into distributable DMGs

**Last updated:** 2026-02-26

The macOS code signing and notarization pipeline is genuinely painful. This skill walks through the whole process so the agent doesn't skip steps or get the order wrong.

**Use for:** SwiftUI/AppKit release pipelines, Developer ID signing, notarytool, DMG creation, debugging codesign failures

```bash
npx skills add jakerains/AgentSkills --skill macos-dmg-builder
```

---

### vercel-workflow
> Build durable, long-running workflows with Vercel's Workflow DevKit

**Last updated:** 2026-01-25

Useful if you're building background jobs, AI agent pipelines, or anything that needs retry logic and multi-step flows on Vercel.

**Use for:** Background jobs, AI agents, webhooks, scheduled tasks, retry logic, multi-step workflows

```bash
npx skills add jakerains/AgentSkills --skill vercel-workflow
```

---

### codex-app-server
> Embed Codex into rich apps with the Codex App Server

**Last updated:** 2026-03-31

Pretty specific to building apps that integrate OpenAI's Codex. If that's your thing, this covers Electron, Swift, Next.js clients, auth flows, and streaming events.

**Use for:** Codex client integration, ChatGPT/API-key login, streamed events, approvals

```bash
npx skills add jakerains/AgentSkills --skill codex-app-server
```

---

### shot-list
> Generate professional shot lists from screenplays

**Last updated:** 2026-01-19

This one is definitely a "Jake skill." I do video production work and needed a way to break down scripts into shot lists. If you're in film/video, it's great. Otherwise, probably not your thing.

**Use for:** Film/video production planning, screenplay breakdowns, shot planning

```bash
npx skills add jakerains/AgentSkills --skill shot-list
```

---

### nextstep-tours
> Product tours and onboarding with NextStep v2 for Next.js

**Last updated:** 2026-04-05

Built this for a specific project. If you're using NextStep for guided tours and onboarding flows, this is exactly what you need. Otherwise you probably won't reach for it.

**Use for:** Guided tours, onboarding flows, feature walkthroughs, interactive tutorials

```bash
npx skills add jakerains/AgentSkills --skill nextstep-tours
```

---

### driverjs-tours
> Product tours, single-element highlights, and pulsing feature hints with Driver.js

**Last updated:** 2026-07-22

The framework-agnostic counterpart to nextstep-tours. Driver.js is a ~5kb, dependency-free library that dims the page, spotlights an element, and shows a popover — works in vanilla JS, React, Next.js, Vue, Svelte, or Angular. This skill is scraped straight from the current driver.js docs: full config/API/state type reference, theming (CSS classes + variables, dark mode, `onPopoverRender`), and copy-paste recipes for click-driven tours, multi-page resumable tours, confirm-on-exit, async navigation, and the separate hints/beacon module.

**Use for:** Guided product tours, onboarding walkthroughs, coach marks, feature spotlights, "what's new" callouts, feature hints/beacons, styling/theming Driver.js popovers and overlays

```bash
npx skills add jakerains/AgentSkills --skill driverjs-tours
```

---

### sam3
> Meta SAM 3 for open-vocabulary image and video segmentation

**Last updated:** 2026-02-26

Another niche one. If you're working with Meta's Segment Anything Model 3, this covers setup, checkpoint auth, segmentation workflows, and fine-tuning. Built it when I was experimenting with SAM3 and the agent kept getting the setup wrong.

**Use for:** SAM3 setup, HuggingFace checkpoint auth, image/video segmentation, fine-tuning

```bash
npx skills add jakerains/AgentSkills --skill sam3
```

---

### worktree-bootstrap
> Make a freshly-created git worktree run its dev server exactly like the main checkout

**Last updated:** 2026-06-29

Built this after a nested git worktree kept hard-freezing my machine when I ran the dev server in it. A worktree only checks out tracked files, so it's missing its gitignored `.env.local` and `node_modules` and the dev server crashes (missing env vars, or `next: command not found`). And for Next.js, a nested worktree can mis-root Turbopack to the parent and watch two dependency trees at once → out of memory → freeze. This copies the env from the main checkout, installs deps with whatever package manager the repo uses (pnpm/npm/yarn/bun), and flags the one-line `turbopack.root` fix when it's missing. Project-agnostic — any JS/TS repo, macOS/Linux/WSL.

**Use for:** setting up / bootstrapping a new git worktree for dev, "worktree missing .env / node_modules", `next: command not found` in a worktree, "inferred workspace root" warning, worktree dev server freezing

```bash
npx skills add jakerains/AgentSkills --skill worktree-bootstrap
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
