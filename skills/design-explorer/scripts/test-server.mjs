#!/usr/bin/env node

import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import test from 'node:test';

const skillDir = new URL('..', import.meta.url).pathname.replace(/\/$/, '');

async function freePort() {
  const server = createServer();
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const { port } = server.address();
  await new Promise((resolve) => server.close(resolve));
  return port;
}

function runNode(file, args, env) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [file, ...args], {
      env: { ...process.env, ...env },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.once('error', reject);
    child.once('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('register preserves quoted project and mockup paths', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const project = join(scratch, 'project "quoted"');
  const mockups = join(scratch, 'mockups "quoted"');
  const port = await freePort();
  await mkdir(project, { recursive: true });

  t.after(async () => {
    await runNode(join(skillDir, 'scripts', 'stop.mjs'), ['--port', String(port)], {
      DESIGN_EXPLORER_STATE_DIR: state,
    });
    await rm(scratch, { recursive: true, force: true });
  });

  const result = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
    '--project', project,
    '--dir', mockups,
    '--port', String(port),
  ], { DESIGN_EXPLORER_STATE_DIR: state });

  assert.equal(result.code, 0, result.stderr);
  const workspaceId = result.stdout.trim();
  assert.ok(workspaceId, 'register should print a workspace id');

  const response = await fetch(
    `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/context`,
  );
  assert.equal(response.status, 200);
  const { workspace } = await response.json();
  assert.equal(workspace.projectPath, project);
  assert.equal(workspace.mockupDir, mockups);

  const pid = (await readFile(join(state, `design-explorer-${port}.pid`), 'utf8')).trim();
  assert.match(pid, /^\d+$/);
});

test('feedback never writes to a project-level signal ledger', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const project = join(scratch, 'project');
  const mockups = join(scratch, 'mockups');
  const ledger = join(project, 'docs', 'design-explorations', 'signal-ledger.jsonl');
  const port = await freePort();
  await mkdir(join(project, 'docs', 'design-explorations'), { recursive: true });
  await writeFile(ledger, '{"sentinel":true}\n');

  t.after(async () => {
    await runNode(join(skillDir, 'scripts', 'stop.mjs'), ['--port', String(port)], {
      DESIGN_EXPLORER_STATE_DIR: state,
    });
    await rm(scratch, { recursive: true, force: true });
  });

  const registration = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
    '--project', project,
    '--dir', mockups,
    '--port', String(port),
  ], {
    DESIGN_EXPLORER_STATE_DIR: state,
    DE_LEDGER_PATH: ledger,
  });
  assert.equal(registration.code, 0, registration.stderr);
  const workspaceId = registration.stdout.trim();

  const response = await fetch(
    `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/feedback`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: '# Design Explorer Feedback\n\n## Ballot\n\n- Layout: A\n',
        ballot: [{
          question: 'Layout', axis: 'density', mode: 'pick',
          winnerId: 'a', winnerName: 'A', reasons: ['clearer'],
        }],
        annotations: [], captures: {}, images: {},
      }),
    },
  );
  assert.equal(response.status, 200, await response.text());
  assert.equal(await readFile(ledger, 'utf8'), '{"sentinel":true}\n');
  assert.match(await readFile(join(mockups, 'signals.jsonl'), 'utf8'), /"question":"Layout"/);
});

test('public runtime exposes no voice secret or model-invocation endpoint', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const project = join(scratch, 'project');
  const mockups = join(scratch, 'mockups');
  const port = await freePort();
  await mkdir(project, { recursive: true });
  await mkdir(join(mockups, 'assets', 'icons'), { recursive: true });
  await writeFile(
    join(mockups, 'assets', 'icons', 'sample.svg'),
    '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>',
  );
  await writeFile(
    join(mockups, 'mockup-asset.html'),
    '<section data-mockup-id="asset" data-label="Asset"><img src="assets/icons/sample.svg"></section>',
  );

  t.after(async () => {
    await runNode(join(skillDir, 'scripts', 'stop.mjs'), ['--port', String(port)], {
      DESIGN_EXPLORER_STATE_DIR: state,
    });
    await rm(scratch, { recursive: true, force: true });
  });

  const registration = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
    '--project', project,
    '--dir', mockups,
    '--port', String(port),
  ], {
    DESIGN_EXPLORER_STATE_DIR: state,
    SONIOX_KEY: 'must-not-reach-browser',
  });
  assert.equal(registration.code, 0, registration.stderr);
  const workspaceId = registration.stdout.trim();

  const health = await (await fetch(`http://127.0.0.1:${port}/health`)).json();
  assert.equal(health.protocol, 'design-explorer.portable.v1');
  assert.equal(Object.hasOwn(health, 'soniox'), false);

  const page = await (await fetch(`http://127.0.0.1:${port}/`)).text();
  assert.doesNotMatch(page, /must-not-reach-browser|marked\.min\.js|highlight\.min\.js/);
  assert.doesNotMatch(page, /<script[^>]+https?:\/\//i);
  for (const file of [
    'tailwindcss-3.4.17.js',
    'lucide-0.468.0.js',
    'html2canvas-1.4.1.min.js',
  ]) {
    const vendor = await fetch(`http://127.0.0.1:${port}/vendor/${file}`);
    assert.equal(vendor.status, 200);
    assert.ok((await vendor.arrayBuffer()).byteLength > 100_000);
  }
  assert.equal((await fetch(`http://127.0.0.1:${port}/favicon.ico`)).status, 204);
  const asset = await fetch(
    `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/assets/icons/sample.svg`,
  );
  assert.equal(asset.status, 200);
  assert.equal(asset.headers.get('content-type'), 'image/svg+xml; charset=utf-8');
  assert.match(await asset.text(), /<svg/);
  const fullView = await (
    await fetch(
      `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/view/mockup-asset`,
    )
  ).text();
  assert.match(
    fullView,
    new RegExp(`/workspace/${workspaceId}/assets/icons/sample\\.svg`),
  );
  assert.equal(
    (await fetch(
      `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/audio/missing`,
    )).status,
    204,
  );

  const chat = await fetch(
    `http://127.0.0.1:${port}/workspace/${encodeURIComponent(workspaceId)}/chat`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'run a model' }),
    },
  );
  assert.equal(chat.status, 404);
});

test('server exits after inactivity even when a workspace remains registered', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const project = join(scratch, 'project');
  const mockups = join(scratch, 'mockups');
  const port = await freePort();
  await mkdir(project, { recursive: true });

  t.after(async () => {
    await runNode(join(skillDir, 'scripts', 'stop.mjs'), ['--port', String(port)], {
      DESIGN_EXPLORER_STATE_DIR: state,
    });
    await rm(scratch, { recursive: true, force: true });
  });

  const registration = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
    '--project', project,
    '--dir', mockups,
    '--port', String(port),
  ], {
    DESIGN_EXPLORER_STATE_DIR: state,
    DE_IDLE_TIMEOUT_MS: '200',
    DE_IDLE_POLL_MS: '50',
  });
  assert.equal(registration.code, 0, registration.stderr);

  await new Promise((resolve) => setTimeout(resolve, 600));
  await assert.rejects(fetch(`http://127.0.0.1:${port}/health`));
});

test('stop refuses to kill a listener that is not the recorded server', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const port = await freePort();
  await mkdir(state, { recursive: true });

  const dummy = spawn(process.execPath, ['-e', [
    'const http=require("http");',
    `const port=${port};`,
    'const server=http.createServer((req,res)=>{',
    'res.setHeader("content-type","application/json");',
    'res.end(JSON.stringify({pid:process.pid,port}));',
    '});',
    'server.listen(port,"127.0.0.1",()=>console.log("ready"));',
  ].join('')], { stdio: ['ignore', 'pipe', 'pipe'] });
  await new Promise((resolve, reject) => {
    dummy.once('error', reject);
    dummy.stdout.once('data', resolve);
  });

  t.after(async () => {
    dummy.kill('SIGTERM');
    await rm(scratch, { recursive: true, force: true });
  });

  await writeFile(join(state, `design-explorer-${port}.pid`), '999999');
  const result = await runNode(join(skillDir, 'scripts', 'stop.mjs'), [
    '--port', String(port),
  ], { DESIGN_EXPLORER_STATE_DIR: state });

  assert.equal(result.code, 1);
  assert.match(result.stderr, /Refusing to stop/);
  const response = await fetch(`http://127.0.0.1:${port}/health`);
  assert.equal(response.status, 200, 'unrelated listener should remain alive');
});

test('register refuses an incompatible listener instead of reusing it', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const project = join(scratch, 'project');
  const mockups = join(scratch, 'mockups');
  const port = await freePort();
  await mkdir(project, { recursive: true });

  const dummy = createServer((socket) => {
    socket.end([
      'HTTP/1.1 200 OK',
      'Content-Type: application/json',
      'Connection: close',
      '',
      JSON.stringify({ protocol: 'design-explorer.academy.v0', pid: process.pid, port }),
    ].join('\r\n'));
  });
  const sockets = new Set();
  dummy.on('connection', (socket) => {
    sockets.add(socket);
    socket.on('close', () => sockets.delete(socket));
  });
  await new Promise((resolve, reject) => {
    dummy.once('error', reject);
    dummy.listen(port, '127.0.0.1', resolve);
  });
  t.after(async () => {
    for (const socket of sockets) socket.destroy();
    await new Promise((resolve) => dummy.close(resolve));
    await rm(scratch, { recursive: true, force: true });
  });

  const result = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
    '--project', project,
    '--dir', mockups,
    '--port', String(port),
  ], { DESIGN_EXPLORER_STATE_DIR: join(scratch, 'state') });

  assert.equal(result.code, 1);
  assert.match(result.stderr, /occupied by an incompatible server/);
});

test('workspace identity separates same-named clones and branches', async (t) => {
  const scratch = await mkdtemp(join(tmpdir(), 'design-explorer-test-'));
  const state = join(scratch, 'state');
  const projectA = join(scratch, 'one', 'repo');
  const projectB = join(scratch, 'two', 'repo');
  const port = await freePort();
  await mkdir(projectA, { recursive: true });
  await mkdir(projectB, { recursive: true });

  t.after(async () => {
    await runNode(join(skillDir, 'scripts', 'stop.mjs'), ['--port', String(port)], {
      DESIGN_EXPLORER_STATE_DIR: state,
    });
    await rm(scratch, { recursive: true, force: true });
  });

  const registrations = [];
  for (const [project, branch, suffix] of [
    [projectA, 'main', 'a-main'],
    [projectB, 'main', 'b-main'],
    [projectA, 'feature/x', 'a-feature'],
  ]) {
    const result = await runNode(join(skillDir, 'scripts', 'register.mjs'), [
      '--project', project,
      '--branch', branch,
      '--dir', join(scratch, 'mockups', suffix),
      '--port', String(port),
    ], { DESIGN_EXPLORER_STATE_DIR: state });
    assert.equal(result.code, 0, result.stderr);
    registrations.push(result.stdout.trim());
  }
  assert.equal(new Set(registrations).size, 3);

  const paths = [];
  for (const [project, branch] of [
    [projectA, 'main'],
    [projectB, 'main'],
    [projectA, 'feature/x'],
  ]) {
    const result = await runNode(join(skillDir, 'scripts', 'workspace-path.mjs'), [
      '--project', project,
      '--branch', branch,
      '--surface', 'settings',
    ], { DESIGN_EXPLORER_STATE_DIR: state });
    assert.equal(result.code, 0, result.stderr);
    paths.push(result.stdout.trim());
  }
  assert.equal(new Set(paths).size, 3);
});
