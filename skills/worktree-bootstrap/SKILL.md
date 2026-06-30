---
name: worktree-bootstrap
description: >-
  Provision a freshly-created git worktree so its dev server runs exactly like the active trunk. FIRST fast-forwards the worktree up to the active trunk (a worktree is pinned to its own frozen branch, so it silently falls behind every trunk commit — "missing commits"), then copies gitignored env files (.env.local, .env) from the main checkout, installs node_modules with the repo's package manager (pnpm/npm/yarn/bun), and — for Next.js — checks the Turbopack workspace-root + allowedDevOrigins pins that prevent nested-worktree dev-server freezes and portless HMR blocks. Use right after creating a worktree (git worktree add, or `claude --worktree`), or whenever a worktree is missing recent commits, fails with missing env vars, "next: command not found", a node_modules-missing error, or an "inferred workspace root" warning. Triggers: set up / bootstrap / provision / prepare / catch up a worktree, "I just made a worktree", "worktree is missing commits / behind trunk", "worktree is missing its .env / node_modules", "make this worktree run like main", "dev server broken in worktree". Works for any JS/TS repo. Manual: /worktree-bootstrap.
---

# worktree-bootstrap

Make a freshly-created git worktree run its dev server **exactly like the active trunk** — in one command. Project-agnostic: works for any JavaScript/TypeScript repo on macOS, Linux, or WSL.

## Why this exists

A linked worktree is pinned to its **own dedicated branch** (git won't let two worktrees share one), and that branch is **frozen at creation** — it never advances, so every commit on the trunk leaves the worktree silently behind ("missing commits"). On top of that, `git worktree add` (and `claude --worktree`) only check out **tracked** files, so a new worktree is also missing the *gitignored* things a dev server needs:

- **Behind the trunk** → the worktree's branch predates recent commits (config pins, lockfile changes, fixes). This skill **fast-forwards it to the trunk first**, so every later step runs on the final tree.
- **`.env.local` / `.env`** → the app crashes at runtime because a required env var is undefined (a database URL, an API key, etc.).
- **`node_modules`** → `pnpm run dev` fails with `next: command not found` (pnpm won't climb to the parent's `node_modules`).

And for **Next.js**, a worktree nested inside another repo can make Turbopack mis-resolve its workspace root to the parent and watch two dependency trees at once — which can exhaust memory and **hard-freeze the machine**. The fix is a one-line source pin (`turbopack.root`); this skill detects when it's missing — though usually it arrives automatically with the catch-up.

## How to run it

From inside the target worktree, run the bundled script:

```bash
bash scripts/setup-worktree.sh
```

(Use the absolute path to this skill's `scripts/setup-worktree.sh` if you're not in the skill directory.) Then relay its summary to the user. The script is **idempotent** — re-running when already current is a clean no-op. Its only history mutation is a strict fast-forward (`git merge --ff-only`) to the local trunk; it never does a non-ff merge, rebase, reset, force, fetch, or pull, and it **skips and continues** whenever a fast-forward isn't safe.

## What it does

1. **Catch up to trunk** — fast-forwards the worktree to the **active trunk** (the branch the primary worktree has checked out, resolved dynamically from `git worktree list` — never hardcoded) via `git merge --ff-only`, so dep-install and the config checks below all run on the final tree. It **skips and continues** (never aborts, never auto-resolves) when the trunk can't be resolved, this worktree *is* the trunk, the tree has uncommitted tracked changes, or the branch has **diverged** (local commits not on the trunk — it tells you to `git rebase` manually).
2. **Env** — copies every gitignored top-level `.env*` file from the **main** checkout into the worktree, only if missing (never overwrites, never prints contents).
3. **Dependencies** — if `node_modules` is absent, detects the package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `package-lock.json` → npm, `yarn.lock` → yarn, `bun.lockb` → bun) and runs the matching install — against the *caught-up* lockfile. With pnpm's shared global store this is typically a few seconds.
4. **Next.js workspace-root check** (read-only) — if a `next.config.*` exists without a `turbopack.root` pin **and** there's a lockfile above the worktree, it warns and prints the fix:
   ```ts
   // next.config.ts — inside nextConfig
   turbopack: { root: import.meta.dirname },
   ```
5. **portless dev-origin check** (read-only) — if `next.config.*` exists and the `portless` CLI is installed, it verifies `allowedDevOrigins` covers portless's multi-label `<branch>.<app>.localhost` host. Next's default `*.localhost` is a *single-label* wildcard, so a two-label portless host gets its dev/HMR requests blocked; if uncovered, it advises the recursive wildcard:
   ```ts
   // next.config.ts — inside nextConfig
   allowedDevOrigins: ["**.localhost"],
   ```

## Why a worktree can be behind

A worktree's branch is frozen at creation, and `claude --worktree` may branch it from the **fork-point** of `main` and your trunk rather than the trunk's current tip — so it predates recent commits, including the Turbopack pins. Step 1 handles this automatically by fast-forwarding to the trunk. It only **can't** when your worktree has diverged (its own commits) or has uncommitted changes — then it tells you exactly what to run.

## The one thing it can't do for you

If your branch has **diverged** from the trunk (you've committed work the trunk doesn't have), step 1 won't fast-forward — that would need a real merge or rebase, which can conflict, so it leaves that to you (`git rebase <trunk>`). And the config pins themselves (`turbopack.root`, `allowedDevOrigins`) are **source code**: if they're genuinely missing from the trunk, add them once on the trunk — every worktree then inherits them via the catch-up.

> Note for monorepos: drop the `turbopack.root: import.meta.dirname` pin when the app lives inside a monorepo — there the root must be the monorepo root, not the app directory.

## Safety

Resolves all paths and the trunk via git (`git rev-parse`, `git worktree list`) — never from user input. Quotes every path, uses no `eval`, and only ever runs `git`, `cp`, and the detected package-manager install. The only history-changing operation is a strict `git merge --ff-only` to a locally-resolved branch — no non-ff merge, rebase, reset, force, fetch, or pull. Env files are copied between two checkouts of the same repo on the same machine; their contents are never transmitted, printed, or logged.
