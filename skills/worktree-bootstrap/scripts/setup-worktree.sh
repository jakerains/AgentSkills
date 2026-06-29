#!/usr/bin/env bash
# worktree-bootstrap — provision a freshly-created git worktree so its dev
# server runs exactly like the main checkout.
#
# Git worktrees only check out *tracked* files, so two things a dev server
# needs are missing in a fresh worktree: gitignored env (.env.local) and
# node_modules. This copies the env from the repo's MAIN checkout, installs
# dependencies with the repo's package manager, and — for Next.js — checks the
# Turbopack workspace-root pin that prevents nested-worktree dev-server freezes.
#
# Portable (Linux/macOS/WSL) and non-fatal: run it from anywhere inside the
# worktree. It never overwrites files, never prints secrets, and only ever
# runs git, cp, and the detected package-manager install.
set -u

say()  { printf '%s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m⚠\033[0m %s\n' "$*"; }

# --- locate the worktree and its main checkout (paths come from git only) -----
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

main=$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2; exit}')
[ -n "${main:-}" ] && main=$(cd "$main" 2>/dev/null && pwd -P)
[ "${main:-}" = "$here" ] && main=""

say "Bootstrapping worktree: $here"
[ -n "${main:-}" ] && say "From main checkout:     $main"
say ""

# --- 1) copy gitignored env files from main -----------------------------------
say "1) Environment files"
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

# --- 2) install node_modules with the repo's package manager ------------------
say "2) Dependencies"
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

# --- 3) Next.js: verify the Turbopack workspace-root pin (read-only) ----------
ncfg=""
for c in next.config.ts next.config.js next.config.mjs next.config.cjs; do
  [ -f "$here/$c" ] && { ncfg="$here/$c"; break; }
done
if [ -n "$ncfg" ]; then
  say "3) Next.js workspace-root check"
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
      warn "no turbopack.root pin, and a lockfile exists ABOVE this worktree ($above)."
      warn "the dev server may mis-root to the parent and watch two trees → memory blow-up / freeze."
      say  "     Fix — add inside nextConfig:  turbopack: { root: import.meta.dirname }"
      say  "     Commit it on the branch you cut worktrees from (your trunk) so they inherit it."
    else
      ok "no parent lockfile detected — root inference is safe here"
    fi
  fi
  say ""

  # --- 4) portless: does allowedDevOrigins cover the worktree's multi-label host? ---
  # portless serves a worktree at `<branch>.<app>.localhost` (two labels before
  # .localhost). Next's default cross-origin allowlist is `*.localhost`, and `*`
  # is a single-label wildcard, so that host is blocked and HMR fails. The fix is
  # a recursive `**.localhost` (or `*.<app>.localhost`) in allowedDevOrigins.
  if command -v portless >/dev/null 2>&1; then
    say "4) portless dev-origin check"
    if grep -qE '(\*\*|\*\.[A-Za-z0-9-]+)\.[A-Za-z0-9.-]*localhost' "$ncfg"; then
      ok "allowedDevOrigins covers portless's <branch>.<app>.localhost hosts"
    else
      app=$(node -e 'try{process.stdout.write((require(process.cwd()+"/package.json").name||"app").replace(/^@[^/]+\//,""))}catch(e){process.stdout.write("app")}' 2>/dev/null || echo app)
      branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g;s/^-//;s/-$//')
      warn "portless serves this worktree near  ${branch:-<branch>}.${app}.localhost  (a multi-label host)."
      warn "Next's default *.localhost wildcard does NOT cover that → dev/HMR requests get blocked."
      say  "     Fix — add inside nextConfig:  allowedDevOrigins: [\"**.localhost\"]"
      say  "     Commit it on the branch you cut worktrees from (your trunk) so they inherit it."
    fi
    say ""
  fi
fi

ok "Worktree ready. Start your dev server (e.g. pnpm dev, or portless)."
