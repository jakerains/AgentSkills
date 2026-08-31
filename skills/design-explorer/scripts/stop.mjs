#!/usr/bin/env node

import { readFile, unlink } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join } from 'node:path';

const portIndex = process.argv.indexOf('--port');
const port = portIndex === -1 ? 10000 : Number.parseInt(process.argv[portIndex + 1], 10);
const stateDir = process.env.DESIGN_EXPLORER_STATE_DIR
  || join(homedir(), '.local', 'state', 'design-explorer');
const pidFile = join(stateDir, `design-explorer-${port}.pid`);

let pid;
try {
  pid = Number.parseInt((await readFile(pidFile, 'utf8')).trim(), 10);
} catch {
  console.log(`No owned Design Explorer server is recorded for port ${port}`);
  process.exit(0);
}

let health = null;
try {
  const response = await fetch(`http://127.0.0.1:${port}/health`);
  if (response.ok) health = await response.json();
} catch {}

if (!health
    || health.protocol !== 'design-explorer.portable.v1'
    || health.pid !== pid
    || health.port !== port) {
  console.error(`Refusing to stop port ${port}: its listener is not the recorded Design Explorer process ${pid}`);
  process.exit(1);
}

process.kill(pid, 'SIGTERM');
for (let i = 0; i < 30; i += 1) {
  try {
    process.kill(pid, 0);
    await new Promise((resolve) => setTimeout(resolve, 50));
  } catch {
    break;
  }
}
await unlink(pidFile).catch(() => {});
console.log(`Stopped Design Explorer on port ${port} (PID ${pid})`);
