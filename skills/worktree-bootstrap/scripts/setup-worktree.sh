#!/usr/bin/env bash
# worktree-bootstrap — provision a freshly-created git worktree so its dev
# server runs exactly like the active trunk.
#
# A linked worktree is pinned to its own dedicated branch (git won't let two
# worktrees share a branch), and that branch is frozen at creation time — it
# never advances on its own, so every commit on the trunk leaves the worktree
# silently behind ("the worktree is missing commits"). So step 1 FAST-FORWARDS
# the worktree to the active trunk; only then does it copy gitignored env from
# the main checkout, install node_modules, and run the Next.js/Turbopack pin
# doctors — so every later step operates on the final, caught-up tree (no
# installing deps against a stale lockfile that catch-up then moves).
#
# Portable (Linux/macOS/WSL) and non-fatal. The ONLY history mutation is a
# strict fast-forward (`git merge --ff-only`) to the LOCAL trunk: never a non-ff
# merge, rebase, reset, force, fetch, or pull. When a fast-forward isn't safe it
# SKIPS (prints why and continues) rather than aborting the bootstrap.
set -u

say()  { printf '%s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m⚠\033[0m %s\n' "$*"; }
info() { printf '  \033[36mℹ\033[0m %s\n' "$*"; }

# --- locate the worktree and the main checkout (paths come from git only) -----
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  say "Not inside a git repository — nothing to do."; exit 0
fi
common_dir=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
git_dir=$(git rev-parse --git-dir 2>/dev/null) || exit 0
common_dir=$(cd "$common_dir" 2>/dev/null && pwd -P) || exit 0
git_dir=$(cd "$git_dir" 2>/dev/null && pwd -P) || exit 0
here=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
here=$(cd "$here" 2>/dev/null && pwd -P) || exit 0

if [ "$common_dir" = "$git_dir" ]; then
  say "This is the PRIMARY checkout, not a linked worktree — nothing to bootstrap."
  say "Run this inside a worktree (git worktree add <path> / claude --worktree)."
  exit 0
fi

# The porcelain worktree list: first block is the PRIMARY (main) worktree.
porcelain=$(git worktree list --porcelain 2>/dev/null)
main=$(printf '%s\n' "$porcelain" | awk '/^worktree /{print $2; exit}')
[ -n "${main:-}" ] && main=$(cd "$main" 2>/dev/null && pwd -P)
[ "${main:-}" = "$here" ] && main=""

say "Bootstrapping worktree: $here"
[ -n "${main:-}" ] && say "Main checkout:          $main"
say ""

# --- 1) catch up to the active trunk (fast-forward only) ----------------------
# The active trunk is whatever branch the PRIMARY worktree has checked out — the
# first block of the porcelain list. Resolved dynamically; never hardcoded (the
# trunk has changed before and will again). Worktrees are pinned to their own
# frozen branch, so without this they drift behind every trunk commit.
say "1) Catch up to trunk"
trunk=$(printf '%s\n' "$porcelain" | awk '
  /^worktree /{n++}
  n==1 && /^branch /{sub("refs/heads/","",$2); print $2; exit}')
cur=$(git branch --show-current 2>/dev/null)

if [ -z "$trunk" ]; then
  warn "could not resolve the trunk (primary worktree detached?) — skipping catch-up."
elif [ "$cur" = "$trunk" ]; then
  info "this worktree is the trunk ($trunk) — nothing to catch up."
elif [ -n "$(git status --porcelain -uno 2>/dev/null)" ]; then
  warn "uncommitted tracked changes present — skipping catch-up to stay safe."
  say  "     When clean:  git merge --ff-only $trunk"
elif ! git merge-base --is-ancestor "$cur" "$trunk" 2>/dev/null; then
  warn "'$cur' has diverged from '$trunk' (it has commits not on the trunk) — NOT fast-forwarding."
  say  "     Rebase manually when ready:  git rebase $trunk"
else
  behind=$(git rev-list --count "HEAD..$trunk" 2>/dev/null); behind=${behind:-0}
  if [ "$behind" -eq 0 ]; then
    ok "already up to date with trunk ($trunk)."
  elif git merge --ff-only "$trunk" >/dev/null 2>&1; then
    ok "caught up $behind commit(s) from trunk ($trunk)."
  else
    warn "fast-forward to '$trunk' failed unexpectedly — skipping (your tree is unchanged)."
  fi
fi
say ""

# --- 2) copy gitignored env files from the main checkout ----------------------
say "2) Environment files"
if [ -n "${main:-}" ]; then
  copied=0
  while IFS= read -r f; do
    [ -f "$main/$f" ] || continue
    if [ -e "$here/$f" ]; then
      say "  $f already present — left as-is"
    elif cp "$main/$f" "$here/$f" 2>/dev/null; then
      ok "copied $f from main"; copied=$((copied+1))
    fi
  done < <(cd "$main" && git ls-files --others --ignored --exclude-standard 2>/dev/null | grep -E '^\.env[^/]*$')
  [ "$copied" -eq 0 ] && say "  (nothing to copy — already set or none gitignored)"
else
  warn "couldn't locate the main checkout — skipping env copy"
fi
say ""

# --- 3) install node_modules with the repo's package manager ------------------
# Runs AFTER catch-up so deps install against the final package.json / lockfile.
say "3) Dependencies"
if [ -e "$here/node_modules" ]; then
  say "  node_modules already present — skipping install"
else
  # Make the toolchain reachable even from a minimal (non-login) shell.
  # Covers macOS (Library/pnpm, Homebrew) and Linux/WSL (.local/share/pnpm).
  for d in "$HOME/Library/pnpm" "$HOME/.local/share/pnpm" "$HOME/.nvm/versions/node"/*/bin \
           /opt/homebrew/bin /usr/local/bin; do
    case ":$PATH:" in *":$d:"*) ;; *) [ -d "$d" ] && PATH="$d:$PATH" ;; esac
  done
  export PATH

  pm=""; args=()
  if   [ -f "$here/pnpm-lock.yaml" ];    then pm=pnpm; args=(install --frozen-lockfile --prefer-offline)
  elif [ -f "$here/package-lock.json" ]; then pm=npm;  args=(ci)
  elif [ -f "$here/yarn.lock" ];         then pm=yarn; args=(install --frozen-lockfile)
  elif [ -f "$here/bun.lockb" ];         then pm=bun;  args=(install)
  fi

  if [ -z "$pm" ]; then
    warn "no lockfile found — skipping dependency install"
  elif ! command -v "$pm" >/dev/null 2>&1; then
    warn "node_modules missing and '$pm' not on PATH — run your install manually"
  else
    say "  running: $pm ${args[*]}"
    if ( cd "$here" && "$pm" "${args[@]}" ); then
      ok "node_modules provisioned via $pm"
    else
      warn "'$pm ${args[*]}' failed — run it manually and re-check"
    fi
  fi
fi
say ""

# --- 4 & 5) Next.js worktree-pin doctors (read-only) --------------------------
# After catch-up these usually pass; a warning here means the pin is genuinely
# absent from the trunk (add it to next.config on the trunk).
ncfg=""
for c in next.config.ts next.config.js next.config.mjs next.config.cjs; do
  [ -f "$here/$c" ] && { ncfg="$here/$c"; break; }
done
if [ -n "$ncfg" ]; then
  say "4) Next.js workspace-root check"
  if grep -qE 'turbopack' "$ncfg" && grep -qE 'root[[:space:]]*:' "$ncfg"; then
    ok "turbopack.root is pinned in $(basename "$ncfg")"
  else
    above=""; d=$(dirname "$here")
    while [ -n "$d" ] && [ "$d" != "/" ]; do
      if [ -f "$d/pnpm-lock.yaml" ] || [ -f "$d/package-lock.json" ] || \
         [ -f "$d/yarn.lock" ] || [ -f "$d/pnpm-workspace.yaml" ]; then above="$d"; break; fi
      d=$(dirname "$d")
    done
    if [ -n "$above" ]; then
      warn "no turbopack.root pin, and a lockfile exists ABOVE this worktree ($above) → dev server may freeze."
      say  "     Add to $(basename "$ncfg") (on the trunk):  turbopack: { root: import.meta.dirname }"
    else
      ok "no parent lockfile detected — root inference is safe here"
    fi
  fi
  say ""

  # portless serves a worktree at `<branch>.<app>.localhost` (two labels before
  # .localhost). Next's default allowlist `*.localhost` is a single-label
  # wildcard, so that host is blocked and HMR fails. Fix: `**.localhost`.
  if command -v portless >/dev/null 2>&1; then
    say "5) portless dev-origin check"
    if grep -qE '(\*\*|\*\.[A-Za-z0-9-]+)\.[A-Za-z0-9.-]*localhost' "$ncfg"; then
      ok "allowedDevOrigins covers portless's <branch>.<app>.localhost hosts"
    else
      warn "no allowedDevOrigins '**.localhost' — portless's multi-label host gets dev/HMR requests blocked."
      say  "     Add to $(basename "$ncfg") (on the trunk):  allowedDevOrigins: [\"**.localhost\"]"
    fi
    say ""
  fi
fi

ok "Worktree ready. Start your dev server (e.g. pnpm dev, or portless)."
