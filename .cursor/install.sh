#!/usr/bin/env bash
# Idempotent bootstrap for the AgentSkills repository.
#
# This repo is a Markdown-centric skills library. Its "application" is the
# Skills CLI (used for scaffolding, installing, and validating skills) plus the
# runnable helper scripts bundled inside individual skills (Node.js and Python).
# The base image already provides Node.js, Python 3, git, jq, zip, and unzip, so
# this script only needs to make the Skills CLI available and confirm the
# toolchain is healthy.
set -euo pipefail

echo "==> AgentSkills environment bootstrap"

# Install the Skills CLI into a user-writable npm prefix (no root needed for the
# install itself) so `skills` / `add-skill` are available as first-class
# commands in addition to the documented `npx skills` usage.
#
# Pass the prefix per-command rather than via `npm config set prefix`: a
# persistent `prefix` in ~/.npmrc is incompatible with the image's nvm setup and
# triggers a warning on every login shell.
NPM_GLOBAL_PREFIX="${HOME}/.npm-global"
mkdir -p "${NPM_GLOBAL_PREFIX}"

echo "==> Installing Skills CLI (skills)"
npm install -g --prefix "${NPM_GLOBAL_PREFIX}" skills

# Expose the CLI on a directory that is already on the login PATH so future
# agents can call `skills` directly without shell-profile changes.
if [ -w /usr/local/bin ] || sudo -n true 2>/dev/null; then
  sudo ln -sf "${NPM_GLOBAL_PREFIX}/bin/skills" /usr/local/bin/skills
  sudo ln -sf "${NPM_GLOBAL_PREFIX}/bin/add-skill" /usr/local/bin/add-skill
else
  echo "    (skipping /usr/local/bin symlink; use 'npx skills' instead)"
fi

echo "==> Toolchain versions"
echo "    node   : $(node --version)"
echo "    npm    : $(npm --version)"
echo "    python : $(python3 --version)"
echo "    git    : $(git --version)"
echo "    skills : $("${NPM_GLOBAL_PREFIX}/bin/skills" --version 2>/dev/null || echo 'via npx skills')"

echo "==> Bootstrap complete"
