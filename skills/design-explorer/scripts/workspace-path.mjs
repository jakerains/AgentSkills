#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i].startsWith('--')) out[argv[i].slice(2)] = argv[++i];
  }
  return out;
}

function slug(value, fallback) {
  return String(value || fallback)
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-')
    .slice(0, 40) || fallback;
}

const args = parseArgs(process.argv.slice(2));
if (!args.project || !args.surface) {
  console.error('Usage: workspace-path.mjs --project /path --surface surface-name [--branch branch]');
  process.exit(1);
}

const project = (() => {
  try { return realpathSync.native(resolve(args.project)); }
  catch { return resolve(args.project); }
})();
let branch = args.branch;
if (!branch) {
  const result = spawnSync('git', ['branch', '--show-current'], {
    cwd: project,
    encoding: 'utf8',
  });
  branch = result.status === 0 && result.stdout.trim() ? result.stdout.trim() : 'default';
}

const projectHash = createHash('sha256').update(project).digest('hex').slice(0, 10);
const branchHash = createHash('sha256').update(branch).digest('hex').slice(0, 8);
const stateDir = process.env.DESIGN_EXPLORER_STATE_DIR
  || join(homedir(), '.local', 'state', 'design-explorer');
const directory = [
  slug(basename(project), 'project'),
  projectHash,
  slug(branch, 'branch'),
  branchHash,
  slug(args.surface, 'surface'),
].join('-');

console.log(join(stateDir, 'mockups', directory));
