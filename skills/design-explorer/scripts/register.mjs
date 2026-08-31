#!/usr/bin/env node

import { mkdir } from 'node:fs/promises';
import { spawn, spawnSync } from 'node:child_process';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

function parseArgs(argv) {
  const out = { port: 10000, tailnet: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--tailnet') out.tailnet = true;
    else if (arg.startsWith('--')) out[arg.slice(2)] = argv[++i];
  }
  out.port = Number.parseInt(String(out.port), 10);
  return out;
}

const protocol = 'design-explorer.portable.v1';

async function health(port) {
  try {
    const response = await fetch(`http://127.0.0.1:${port}/health`);
    return response.ok ? response.json() : null;
  } catch {
    return null;
  }
}

const args = parseArgs(process.argv.slice(2));
if (!args.project || !args.dir || !Number.isInteger(args.port)) {
  console.error('Usage: register.mjs --project /path --dir /path/mockups [--branch main] [--port 10000] [--tailnet]');
  process.exit(1);
}

const stateDir = process.env.DESIGN_EXPLORER_STATE_DIR
  || join(homedir(), '.local', 'state', 'design-explorer');
const skillDir = dirname(dirname(fileURLToPath(import.meta.url)));
const serverPath = join(skillDir, 'assets', 'server.cjs');
await mkdir(args.dir, { recursive: true });
await mkdir(stateDir, { recursive: true });

let current = await health(args.port);
if (current && current.protocol !== protocol) {
  console.error(`Port ${args.port} is occupied by an incompatible server. Stop that server or choose another port.`);
  process.exit(1);
}
if (!current) {
  const child = spawn(process.execPath, [
    serverPath,
    '--port', String(args.port),
    '--no-open',
    ...(args.tailnet ? ['--tailnet'] : []),
  ], {
    detached: true,
    stdio: 'ignore',
    env: { ...process.env, DESIGN_EXPLORER_STATE_DIR: stateDir },
  });
  child.unref();

  const deadline = Date.now() + 5000;
  while (!current && Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    current = await health(args.port);
  }
}

if (!current) {
  console.error(`Design Explorer did not start on port ${args.port}`);
  process.exit(1);
}
if (current.protocol !== protocol) {
  console.error(`Port ${args.port} did not start the expected Design Explorer protocol.`);
  process.exit(1);
}
if (args.tailnet && !current.tailnet) {
  console.error('Design Explorer is already running without tailnet access. Stop it, then register again with --tailnet.');
  process.exit(1);
}

let branch = args.branch;
if (!branch) {
  const result = spawnSync('git', ['branch', '--show-current'], {
    cwd: args.project,
    encoding: 'utf8',
  });
  branch = result.status === 0 && result.stdout.trim() ? result.stdout.trim() : 'default';
}

const response = await fetch(`http://127.0.0.1:${args.port}/workspace/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    projectPath: args.project,
    branch,
    mockupDir: args.dir,
  }),
});
const body = await response.json().catch(() => ({}));
if (!response.ok || !body.id) {
  console.error(body.note || body.error || `Workspace registration failed (${response.status})`);
  process.exit(1);
}

console.log(body.id);
