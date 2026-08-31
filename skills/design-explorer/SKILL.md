---
name: design-explorer
description: "Explore genuinely open UI or layout directions by generating 6-10 HTML fragments and reviewing them in a local voting and annotation carousel. Use for requests like 'show me layout options', 'mock up variations', 'compare UI directions', 'A/B these designs', or when several visual approaches should be judged before implementation. Keeps an existing product's design system fixed while varying layout grammar, captures every submitted design as PNG and HTML, and records votes, notes, pins, drawings, rankings, and reasons. Preview-only: never treat the mockups as production code."
---

# Design Explorer

Compare several plausible directions before committing to one. Generate throwaway HTML fragments, review them at **http://127.0.0.1:10000**, read the captured evidence, then implement the winning ideas in the real product.

This skill is a vendored MIT fork of **houshuang/design-explorer**; see **LICENSE**. Its local server has no npm dependencies and binds to loopback unless tailnet access is explicitly requested.

## 1. Establish what is fixed

Read the repo's design guidance, tokens, agent instructions, component layer, and two or three shipped screens. State the fixed constraints before generating: palette, type, spacing, elevation, voice, and accessibility floor.

If a design system exists, vary layout grammar rather than brand identity:

- density and whitespace
- scan order and hierarchy
- progressive disclosure
- navigation and control affordances
- media placement
- interaction posture

If no design system exists, say that clearly. A broader visual-direction round is then appropriate.

## 2. Register a workspace

Require Node.js 18 or newer. Set **SKILL_DIR** to the absolute directory containing this loaded **SKILL.md**; do not assume the skill lives inside the current repo.

~~~bash
SKILL_DIR="<absolute directory containing this SKILL.md>"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
MOCKUP_DIR="$(node "$SKILL_DIR/scripts/workspace-path.mjs" --project "$PROJECT_ROOT" --surface "<surface>")"
WORKSPACE_ID="$(node "$SKILL_DIR/scripts/register.mjs" --project "$PROJECT_ROOT" --dir "$MOCKUP_DIR")"
~~~

The path helper includes the canonical project path and branch in the directory identity, so same-named clones and branches cannot share review evidence. The register script creates the directory and starts the server if needed. It refuses an older or unrelated listener on the requested port. Keep workspaces outside the repo by default. Do not add review artifacts, notes, or signal ledgers to the project tree without the user's permission.

If port 10000 is occupied by an incompatible server, leave that process alone and choose a free port with **--port**. Use the same port in the review URL and all register, status, and stop commands.

## 3. Generate 6-10 directions

Create files named **mockup-{descriptive-slug}.html** in **MOCKUP_DIR**. Each file must contain one bare fragment and no page boilerplate:

~~~html
<section data-mockup-id="compact-rail" data-label="Compact rail">
  <!-- realistic product content -->
</section>
~~~

Use real product language, not lorem ipsum. Make each direction meaningfully different on one or more stated layout dimensions while keeping fixed constraints intact. Mockups are reference material, not code to copy into production.

Put local images, fonts, audio, or video used by mockups under **MOCKUP_DIR/assets/**. References beginning with **/assets/** are rewritten to a workspace-scoped read-only route, so different review workspaces cannot collide.

The skill bundles exact Tailwind CSS, Lucide, and html2canvas browser builds. Google Fonts use the network when available and fall back to system fonts when unavailable. The local Node server makes no model calls and needs no paid API key.

## 4. Review

Open **http://127.0.0.1:10000** and select the workspace.

- Arrow keys navigate.
- Up and down vote.
- Tab focuses the note field.
- **P** adds a positioned note.
- **D** draws; hold Shift for a box.
- **C** submits the round.

Use Explore mode for broad reactions. Use a **round.json** ballot when the reviewer needs to pick or rank explicit alternatives. See **references/review-modes.md**.

## 5. Read the evidence before iterating

Every submitted design is captured, whether or not it received a vote or annotation. Read all four artifacts:

1. **captures/<mockup-id>.png** — inspect this first for spatial meaning.
2. **annotations.json** — structured pins, targets, drawings, and capture paths.
3. **feedback.md** — votes, notes, and readable annotation summary.
4. **captures/<mockup-id>.html** — searchable DOM snapshot.

Capture lazy-loads the bundled html2canvas build from the local server. If capture fails, report it; do not pretend the text artifacts prove the visual result.

Refine liked directions, remove rejected ones, and create hybrids or controlled challengers. Repeat until the evidence supports a direction. Do not simply reshuffle survivors.

## 6. Hand off deliberately

Explain the winning direction, the evidence supporting it, and which ideas should become real components. Ask before writing a durable handoff inside the repo. Re-implement the accepted pattern using the project's component, accessibility, typing, and testing conventions.

Never ship the mockup fragment itself as production code.

## Optional access and advanced review

For phone or tablet review, restart the server with **--tailnet**:

~~~bash
node "$SKILL_DIR/scripts/stop.mjs"
WORKSPACE_ID="$(node "$SKILL_DIR/scripts/register.mjs" --project "$PROJECT_ROOT" --dir "$MOCKUP_DIR" --tailnet)"
node "$SKILL_DIR/scripts/status.mjs"
~~~

Tailnet mode adds a listener on the machine's Tailscale address. Review and write endpoints are unauthenticated, so use it only on a trusted personal tailnet. It never binds to **0.0.0.0**.

See **references/capture-mobile-presentations.md** for touch review, guided presentations, capture details, and convergence guidance.

## Housekeeping

- **node "$SKILL_DIR/scripts/status.mjs"** shows the owned server and workspaces.
- **node "$SKILL_DIR/scripts/stop.mjs"** stops only the recorded Design Explorer process.
- The server idles out after 30 minutes without requests, review streams, or workspace activity.
- Override the state root with **DESIGN_EXPLORER_STATE_DIR** and the port with **--port**.
- Do not add chat, model invocation, voice transcription, secrets, or automatic repo writes to the review surface.
