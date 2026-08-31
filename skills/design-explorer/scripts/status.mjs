#!/usr/bin/env node

const portIndex = process.argv.indexOf('--port');
const port = portIndex === -1 ? 10000 : Number.parseInt(process.argv[portIndex + 1], 10);

try {
  const response = await fetch(`http://127.0.0.1:${port}/health`);
  if (!response.ok) throw new Error();
  const health = await response.json();
  if (health.protocol !== 'design-explorer.portable.v1') {
    throw new Error('incompatible listener');
  }
  console.log(`PID: ${health.pid}  Port: ${health.port}  Tailnet: ${health.tailnet || 'off'}`);
  console.log(`Workspaces: ${health.workspaces.length}`);
  for (const ws of health.workspaces) {
    console.log(`  - ${ws.id}  ${ws.mockups} mockups  ${ws.sessions} sessions  ${ws.mockupDir}`);
  }
} catch {
  console.error(`Design Explorer is not running on port ${port}`);
  process.exit(1);
}
