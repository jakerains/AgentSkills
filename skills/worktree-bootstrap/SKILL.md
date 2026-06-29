---
name: worktree-bootstrap
description: >-
  Provision a freshly-created git worktree so its dev server runs exactly like the main checkout. Copies gitignored env files (.env.local, .env) from the main worktree, installs node_modules with the repo's package manager (pnpm/npm/yarn/bun), and — for Next.js projects — checks the Turbopack workspace-root pin that prevents nested-worktree dev-server freezes. Use right after creating a worktree (git worktree add, or `claude --worktree`), or whenever a worktree's dev server fails with missing env vars, "next: command not found", a node_modules-missing error, or an "inferred workspace root" warning. Triggers: set up / bootstrap / provision / prepare a worktree, "I just made a worktree", "worktree is missing its .env / node_modules", "make this worktree run like main", "dev server broken in worktree". Works for any JS/TS repo. Manual: /worktree-bootstrap.
---

# worktree-bootstrap

Make a freshly-created git worktree run its dev server **exactly like the main checkout** — in one command. Project-agnostic: works for any JavaScript/TypeScript repo on macOS, Linux, or WSL.

## Why this exists

`git worktree add` (and `claude --worktree`) only check out **tracked** files. Two things a dev server needs are *gitignored*, so a new worktree is missing them and the dev server breaks:

- **`.env.local` / `.env`** → the app crashes at runtime because a required env var is undefined (a database URL, an API key, etc.).
- **`node_modules`** → `pnpm run dev` fails with `next: command not found` (pnpm won't climb to the parent's `node_modules`).

And for **Next.js**, a worktree nested inside another repo can make Turbopack mis-resolve its workspace root to the parent and watch two dependency trees at once — which can exhaust memory and **hard-freeze the machine**. The fix is a one-line source pin (see step 3); this skill detects when it's missing.

## How to run it

From inside the target worktree, run the bundled script:

```bash
bash scripts/setup-worktree.sh
```

(Use the absolute path to this skill's `scripts/setup-worktree.sh` if you're not in the skill directory.) Then relay its summary to the user. The script is idempotent and non-destructive — safe to run more than once.

## What it does

1. **Env** — copies every gitignored top-level `.env*` file from the **main** checkout into the worktree, only if missing (never overwrites, never prints contents).
2. **Dependencies** — if `node_modules` is absent, detects the package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `package-lock.json` → npm, `yarn.lock` → yarn, `bun.lockb` → bun) and runs the matching install. With pnpm's shared global store this is typically a few seconds.
3. **Next.js doctor** (read-only) — if a `next.config.*` exists without a `turbopack.root` pin **and** there's a lockfile above the worktree, it warns and prints the fix:
   ```ts
   // next.config.ts — inside nextConfig
   turbopack: { root: import.meta.dirname },
   ```
4. **portless dev-origin check** (read-only) — if `next.config.*` exists and the `portless` CLI is installed, it verifies `allowedDevOrigins` covers portless's multi-label `<branch>.<app>.localhost` host. Next's default `*.localhost` is a *single-label* wildcard, so a two-label portless host gets its dev/HMR requests blocked; if uncovered, it advises the recursive wildcard:
   ```ts
   // next.config.ts — inside nextConfig
   allowedDevOrigins: ["**.localhost"],
   ```

## The one thing it can't do for you

Steps 3 and 4 only **detect** missing config — they can't add it, because those are **source-code** changes (`turbopack.root` and `allowedDevOrigins`) that must be committed on the branch you cut worktrees from (your trunk) so every new worktree inherits them. Add them once; after that, new worktrees just need this skill for env + deps.

> Note for monorepos: drop the `turbopack.root: import.meta.dirname` pin when the app lives inside a monorepo — there the root must be the monorepo root, not the app directory.

## Safety

Resolves all paths via git (`git rev-parse`, `git worktree list`) — never from user input. Quotes every path, uses no `eval`, and only ever runs `git`, `cp`, and the detected package-manager install. Env files are copied between two checkouts of the same repo on the same machine; their contents are never transmitted, printed, or logged.
