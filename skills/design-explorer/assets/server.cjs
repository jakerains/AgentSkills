#!/usr/bin/env node
// Design Explorer — Global Singleton Server (zero dependencies)
// Manages multiple workspaces, one per project/branch.
// Usage: node server.js [--port 10000] [--no-open]

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { exec } = require('child_process');
const os = require('os');

// ── Config ──────────────────────────────────────
const args = process.argv.slice(2);
function getArg(name, fallback) {
  const i = args.indexOf('--' + name);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
}
const PORT = parseInt(getArg('port', '10000'), 10);
const NO_OPEN = args.includes('--no-open');
const WANT_TAILNET = args.includes('--tailnet');
const IDLE_TIMEOUT_MS = parseInt(process.env.DE_IDLE_TIMEOUT_MS || String(30 * 60 * 1000), 10);
const IDLE_POLL_MS = parseInt(process.env.DE_IDLE_POLL_MS || String(60 * 1000), 10);
const HARNESS = path.join(__dirname, 'harness-template.html');
const VENDOR_FILES = new Map([
  ['/vendor/tailwindcss-3.4.17.js', ['tailwindcss-3.4.17.js', 'text/javascript; charset=utf-8']],
  ['/vendor/lucide-0.468.0.js', ['lucide-0.468.0.js', 'text/javascript; charset=utf-8']],
  ['/vendor/html2canvas-1.4.1.min.js', ['html2canvas-1.4.1.min.js', 'text/javascript; charset=utf-8']],
]);
const STATE_DIR = process.env.DESIGN_EXPLORER_STATE_DIR
  || path.join(os.homedir(), '.local', 'state', 'design-explorer');
const PID_FILE = path.join(STATE_DIR, `design-explorer-${PORT}.pid`);
const PROTOCOL = 'design-explorer.portable.v1';

// ── Legacy mode: if --dir is passed, run as single-workspace server ──
const LEGACY_DIR = getArg('dir', null);

// ── PID file ────────────────────────────────────
try {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.writeFileSync(PID_FILE, String(process.pid));
} catch {}
function cleanup() {
  try {
    for (const ws of workspaces.values()) stopWatching(ws);
  } catch {}
  try {
    if (fs.readFileSync(PID_FILE, 'utf8').trim() === String(process.pid)) fs.unlinkSync(PID_FILE);
  } catch {}
  process.exit(0);
}
process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);

// ── Workspace Registry ──────────────────────────
const workspaces = new Map(); // id → Workspace
const clients = [];           // [{res, workspaceId}]
let lastActivity = Date.now();

function makeWorkspaceId(projectPath, branch) {
  const name = path.basename(projectPath);
  let canonicalProject;
  try { canonicalProject = fs.realpathSync.native(path.resolve(projectPath)); }
  catch { canonicalProject = path.resolve(projectPath); }
  const branchName = branch || 'default';
  const clean = branchName.replace(/[^a-zA-Z0-9-]/g, '-').replace(/-+/g, '-').slice(0, 24);
  const projectHash = crypto.createHash('sha256').update(canonicalProject).digest('hex').slice(0, 10);
  const branchHash = crypto.createHash('sha256').update(branchName).digest('hex').slice(0, 8);
  return `${name}-${projectHash}-${clean || 'branch'}-${branchHash}`;
}

function isMockup(f) {
  return f.endsWith('.html') && f !== 'harness-template.html';
}

function rewriteWorkspaceAssetUrls(html, workspaceId) {
  const prefix = `/workspace/${encodeURIComponent(workspaceId)}/assets/`;
  return String(html)
    .replace(/(["'])\/?assets\//g, `$1${prefix}`)
    .replace(/url\(\s*(["']?)\/?assets\//gi, `url($1${prefix}`);
}

function assetContentType(file) {
  return ({
    '.avif': 'image/avif',
    '.css': 'text/css; charset=utf-8',
    '.gif': 'image/gif',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.json': 'application/json; charset=utf-8',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.png': 'image/png',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.webm': 'video/webm',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
  })[path.extname(file).toLowerCase()] || 'application/octet-stream';
}

function workspaceAssetFile(ws, relativePath) {
  try {
    const root = fs.realpathSync.native(path.join(ws.mockupDir, 'assets'));
    const candidate = path.resolve(root, relativePath);
    if (candidate !== root && !candidate.startsWith(root + path.sep)) return null;
    const physical = fs.realpathSync.native(candidate);
    if (!physical.startsWith(root + path.sep)) return null;
    return fs.statSync(physical).isFile() ? physical : null;
  } catch {
    return null;
  }
}

function sessionForMockup(ws, mockupId) {
  for (const s of ws.sessions) {
    if (s.mockups.includes(mockupId)) return s.id;
  }
  return null;
}

function saveSessions(ws) {
  try {
    fs.writeFileSync(
      path.join(ws.mockupDir, 'sessions.json'),
      JSON.stringify(ws.sessions, null, 2)
    );
  } catch {}
}

// ── Review rounds: ballots and signals ───────────
// round.json is the question the agent asked; ballot.json is the answer;
// signals.jsonl is the append-only trail across every round in a workspace.
// v2 adds per-matchup mode (pick or rank), an axis slug, and reason chips.
// v1 ballots carried only {question, winnerId, ...} so every new field is
// optional on read and simply comes back empty.
function readRound(ws) {
  try {
    return JSON.parse(fs.readFileSync(path.join(ws.mockupDir, 'round.json'), 'utf8'));
  } catch { return null; }
}

function matchupFor(round, entry, index) {
  if (!round || !Array.isArray(round.matchups)) return null;
  if (entry && entry.question) {
    const byQuestion = round.matchups.find(m => m && m.question === entry.question);
    if (byQuestion) return byQuestion;
  }
  return round.matchups[index] || null;
}

function optionIdsFor(matchup, entry) {
  if (matchup && Array.isArray(matchup.options)) {
    // v1 rounds list bare id strings; v2 lists {id, name, hint} objects.
    const ids = matchup.options
      .map(o => (typeof o === 'string' ? o : (o && o.id ? String(o.id) : '')))
      .filter(Boolean);
    if (ids.length) return ids;
  }
  if (Array.isArray(entry.optionIds)) return entry.optionIds.map(String);
  if (Array.isArray(entry.order)) return entry.order.map(String);
  if (entry.winnerId) return [String(entry.winnerId)];
  return [];
}

function cleanReasons(value) {
  if (!Array.isArray(value)) return [];
  const seen = new Set();
  const out = [];
  for (const r of value) {
    if (typeof r !== 'string') continue;
    const trimmed = r.trim();
    if (!trimmed || seen.has(trimmed)) continue;
    seen.add(trimmed);
    out.push(trimmed);
  }
  return out;
}

function cleanNote(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

// One ballot entry in, one canonical entry out. Rank entries keep their order,
// pick entries keep their winner, and both carry axis, reasons, and note.
function normalizeBallotEntry(entry, matchup) {
  const rank = entry.mode === 'rank'
    || (entry.mode !== 'pick' && Array.isArray(entry.order) && entry.order.length > 0);
  const axis = entry.axis || (matchup && matchup.axis) || '';
  const base = {
    question: entry.question || (matchup && matchup.question) || '',
    axis,
    mode: rank ? 'rank' : 'pick',
  };
  const reasons = cleanReasons(entry.reasons);
  const note = cleanNote(entry.note);

  if (rank) {
    const order = (Array.isArray(entry.order) ? entry.order : []).map(String);
    const orderNames = Array.isArray(entry.orderNames)
      ? entry.orderNames.map(String)
      : order.map((id) => {
          const opt = matchup && Array.isArray(matchup.options)
            ? matchup.options.find(o => o && String(o.id) === id) : null;
          return opt && opt.name ? String(opt.name) : id;
        });
    const out = { ...base, order, orderNames, reasons };
    if (note) out.note = note;
    return out;
  }

  const winnerId = entry.winnerId ? String(entry.winnerId) : '';
  const opt = matchup && Array.isArray(matchup.options)
    ? matchup.options.find(o => o && String(o.id) === winnerId) : null;
  const out = {
    ...base,
    winnerId,
    winnerLabel: entry.winnerLabel != null ? String(entry.winnerLabel) : '',
    winnerName: entry.winnerName != null
      ? String(entry.winnerName)
      : (opt && opt.name ? String(opt.name) : winnerId),
    reasons,
  };
  // "Neither": a full-round rejection — every option loses, and the why-not
  // note is the signal the next generation regenerates from.
  if (entry.neither) { out.neither = true; out.winnerName = 'Neither'; }
  if (Array.isArray(entry.optionIds)) out.optionIds = entry.optionIds.map(String);
  if (note) out.note = note;
  return out;
}

// Append-only workspace signal log. Every matchup answered in this workspace
// lands beside the mockups so later rounds can reuse the reviewer's choices.
function signalLineId(wsKey, question, winner, ts) {
  return crypto.createHash('sha256')
    .update(`${wsKey}|${question}|${winner}|${ts}`)
    .digest('hex').slice(0, 12);
}

// Registrations keep their requested path for the API and file operations, but
// the physical directory owns the signal key. A symlink alias must therefore
// compare as the same workspace directory and produce the same `workspace`
// value in a signal line. A not-yet-created directory has no realpath, so its
// resolved path is its stable identity until it exists.
function physicalMockupDir(mockupDir) {
  const resolved = path.resolve(mockupDir);
  try {
    const realpath = fs.realpathSync.native || fs.realpathSync;
    return realpath(resolved);
  } catch {
    return resolved;
  }
}

function appendJsonLines(file, lines) {
  let prefix = '';
  try {
    const size = fs.statSync(file).size;
    if (size > 0) {
      const fd = fs.openSync(file, 'r');
      try {
        const last = Buffer.allocUnsafe(1);
        fs.readSync(fd, last, 0, 1, size - 1);
        if (last[0] !== 0x0a) prefix = '\n';
      } finally { fs.closeSync(fd); }
    }
  } catch {}
  fs.appendFileSync(file, prefix + lines.join('\n') + '\n');
}

function appendSignals(ws, entries, extra) {
  if (!entries.length) return;
  const ts = new Date().toISOString();
  const wsKey = path.basename(physicalMockupDir(ws.mockupDir));
  const lines = entries.map(({ picked, matchup }) => {
    const optionIds = optionIdsFor(matchup, picked);
    const line = {
      ts,
      workspace: wsKey,
      workspaceLabel: ws.id,
      axis: picked.axis || '',
      mode: picked.mode,
      question: picked.question || '',
    };
    let winnerKey;
    if (picked.mode === 'rank') {
      line.order = picked.order;
      line.losers = optionIds.filter(id => id !== picked.order[0]);
      winnerKey = picked.order[0] || '';
    } else if (picked.neither) {
      line.neither = true;
      line.winnerId = null;
      line.losers = optionIds;
      winnerKey = 'neither';
    } else {
      line.winnerId = picked.winnerId;
      line.losers = optionIds.filter(id => id !== picked.winnerId);
      winnerKey = picked.winnerId;
    }
    line.reasons = picked.reasons;
    if (picked.note) line.note = picked.note;
    line.optionCount = optionIds.length;
    line.source = 'design-explorer';
    line.lineId = signalLineId(wsKey, line.question, winnerKey, ts);
    if (extra) Object.assign(line, extra);
    return JSON.stringify(line);
  });
  const status = { workspace: true };
  try {
    appendJsonLines(path.join(ws.mockupDir, 'signals.jsonl'), lines);
  } catch { status.workspace = false; }
  return status;
}

function getOrCreateOpenSession(ws) {
  if (ws.openSessionId !== null) {
    const session = ws.sessions.find(s => s.id === ws.openSessionId);
    if (session && !session.closed) return session;
  }
  const session = {
    id: ws.nextSession++,
    created: new Date().toISOString(),
    mockups: [],
    closed: false,
  };
  ws.sessions.push(session);
  ws.openSessionId = session.id;
  saveSessions(ws);
  broadcastToWorkspace(ws.id, 'session', { ...session, workspace: ws.id });
  return session;
}

// The deck order the client receives. Alphabetical filename order is only the
// fallback: when the workspace carries a presentation.json, the explorer must
// page through the SAME sequence the walkthrough narrates — otherwise "1 / 18"
// in free browsing and stop 1 of the walkthrough are different mockups, the
// Present button's start-where-parked mapping lands mid-story, and the
// walkthrough counter hops around the deck. Rank = first appearance across the
// stops (anchor first, then contenders); unranked mockups keep filename order
// after the ranked ones.
function presentationOrderRank(ws) {
  try {
    const preso = JSON.parse(fs.readFileSync(path.join(ws.mockupDir, 'presentation.json'), 'utf8'));
    const rank = new Map();
    for (const stop of (Array.isArray(preso.stops) ? preso.stops : [])) {
      const ids = [stop.mockupId].concat(Array.isArray(stop.compare) ? stop.compare : []);
      for (const id of ids) {
        if (typeof id === 'string' && id && !rank.has(id)) rank.set(id, rank.size);
      }
    }
    return rank;
  } catch { return new Map(); }
}

function scanWorkspace(ws) {
  let files;
  try { files = fs.readdirSync(ws.mockupDir).filter(isMockup).sort(); }
  catch { return []; }
  const rank = presentationOrderRank(ws);
  if (rank.size) {
    const rankOf = (file) => {
      const r = rank.get(file.replace('.html', ''));
      return r === undefined ? Number.MAX_SAFE_INTEGER : r;
    };
    files.sort((a, b) => rankOf(a) - rankOf(b));   // stable: ties keep filename order
  }

  const currentFiles = new Set(files);
  const changes = [];

  for (const file of files) {
    const filePath = path.join(ws.mockupDir, file);
    let stat;
    try { stat = fs.statSync(filePath); } catch { continue; }
    const existing = ws.knownFiles.get(file);

    if (!existing) {
      const html = fs.readFileSync(filePath, 'utf8');
      const id = file.replace('.html', '');
      let sessionId = sessionForMockup(ws, id);
      if (sessionId === null) {
        const session = getOrCreateOpenSession(ws);
        if (!session.mockups.includes(id)) {
          session.mockups.push(id);
          saveSessions(ws);
        }
        sessionId = session.id;
      }
      ws.knownFiles.set(file, { mtime: stat.mtimeMs, html, session: sessionId });
      changes.push({
        type: 'add',
        id,
        html: rewriteWorkspaceAssetUrls(html, ws.id),
        session: sessionId,
        workspace: ws.id,
      });
    } else if (stat.mtimeMs > existing.mtime) {
      const html = fs.readFileSync(filePath, 'utf8');
      ws.knownFiles.set(file, { ...existing, mtime: stat.mtimeMs, html });
      changes.push({
        type: 'update',
        id: file.replace('.html', ''),
        html: rewriteWorkspaceAssetUrls(html, ws.id),
        workspace: ws.id,
      });
    }
  }

  for (const [file] of ws.knownFiles) {
    if (!currentFiles.has(file)) {
      changes.push({ type: 'remove', id: file.replace('.html', ''), workspace: ws.id });
      ws.knownFiles.delete(file);
    }
  }

  // Reset sessions when all mockups are deleted (clean start)
  if (ws.knownFiles.size === 0 && ws.sessions.length > 0) {
    ws.sessions = [];
    ws.nextSession = 1;
    ws.openSessionId = null;
    saveSessions(ws);
  }

  ws.lastActive = Date.now();
  return changes;
}

function pushWorkspaceChanges(ws) {
  if (workspaces.get(ws.id) !== ws) return;
  for (const change of scanWorkspace(ws)) {
    broadcastToWorkspace(ws.id, change.type, change);
  }
}

// ── Watching ─────────────────────────────────────
function startWatching(ws) {
  try { fs.mkdirSync(ws.mockupDir, { recursive: true }); } catch {}
  scanWorkspace(ws);

  try {
    ws.watcher = fs.watch(ws.mockupDir, () => {
      ws.watchWorking = true;
      if (ws.watchTimeout) clearTimeout(ws.watchTimeout);
      ws.watchTimeout = setTimeout(() => pushWorkspaceChanges(ws), 200);
    });
  } catch {}

  ws.pollTimer = setInterval(() => {
    if (!ws.watchWorking) pushWorkspaceChanges(ws);
  }, 1500);
  ws.slowPollTimer = setInterval(() => pushWorkspaceChanges(ws), 5000);
}

function stopWatching(ws) {
  if (ws.watcher) { ws.watcher.close(); ws.watcher = null; }
  if (ws.watchTimeout) clearTimeout(ws.watchTimeout);
  ws.watchTimeout = null;
  if (ws.pollTimer) { clearInterval(ws.pollTimer); ws.pollTimer = null; }
  if (ws.slowPollTimer) { clearInterval(ws.slowPollTimer); ws.slowPollTimer = null; }
}

function createWorkspace(projectPath, branch, mockupDir) {
  const id = makeWorkspaceId(projectPath, branch);
  const requestedMockupDir = path.resolve(mockupDir);
  const requestedPhysicalMockupDir = physicalMockupDir(requestedMockupDir);

  if (workspaces.has(id)) {
    const ws = workspaces.get(id);
    if (path.resolve(ws.projectPath) !== path.resolve(projectPath)
        || ws.branch !== (branch || 'default')) {
      const conflict = new Error('derived workspace id already belongs to a different project or branch');
      conflict.code = 'workspace-id-collision';
      throw conflict;
    }
    if (physicalMockupDir(ws.mockupDir) !== requestedPhysicalMockupDir) {
      const conflict = new Error(
        'project and branch are already registered to another mockupDir; '
        + 'use a distinct branch or explicitly deregister the existing workspace before takeover',
      );
      conflict.code = 'workspace-directory-conflict';
      conflict.currentMockupDir = ws.mockupDir;
      conflict.requestedMockupDir = requestedMockupDir;
      throw conflict;
    }
    ws.lastActive = Date.now();
    return ws;
  }

  // Workspace basenames become the durable signal-ledger join key. Do not let
  // distinct physical directories share one, even if their project/branch
  // identities differ; aliases of the same physical directory remain valid.
  const requestedBasename = path.basename(requestedPhysicalMockupDir);
  for (const existing of workspaces.values()) {
    const existingPhysicalMockupDir = physicalMockupDir(existing.mockupDir);
    if (path.basename(existingPhysicalMockupDir) !== requestedBasename
        || existingPhysicalMockupDir === requestedPhysicalMockupDir) continue;
    const conflict = new Error(
      'mockupDir basename is already registered to another physical directory; '
      + 'use a unique mockupDir basename or reuse the existing directory',
    );
    conflict.code = 'workspace-directory-basename-conflict';
    conflict.currentMockupDir = existing.mockupDir;
    conflict.requestedMockupDir = requestedMockupDir;
    throw conflict;
  }

  const ws = {
    id,
    projectPath,
    projectName: path.basename(projectPath),
    branch: branch || 'default',
    mockupDir: requestedMockupDir,
    knownFiles: new Map(),
    sessions: [],
    nextSession: 1,
    lastActive: Date.now(),
    watcher: null, watchTimeout: null, watchWorking: false,
    pollTimer: null, slowPollTimer: null,
    openSessionId: null,
    batching: false,
  };

  // Load existing sessions
  try {
    ws.sessions = JSON.parse(fs.readFileSync(path.join(ws.mockupDir, 'sessions.json'), 'utf8'));
    ws.nextSession = ws.sessions.length > 0
      ? Math.max(...ws.sessions.map(s => s.id)) + 1 : 1;
    const lastSession = ws.sessions[ws.sessions.length - 1];
    if (lastSession && !lastSession.closed) {
      ws.openSessionId = lastSession.id;
    }
  } catch {}

  startWatching(ws);
  workspaces.set(id, ws);
  broadcastGlobal('workspace-add', { id, projectName: ws.projectName, branch: ws.branch });
  return ws;
}

function removeWorkspace(id) {
  const ws = workspaces.get(id);
  if (!ws) return;
  stopWatching(ws);
  workspaces.delete(id);
  broadcastGlobal('workspace-remove', { id });
}

// ── SSE Broadcasting ─────────────────────────────
function broadcastToWorkspace(workspaceId, event, data) {
  const msg = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const c of clients) {
    if (!c.workspaceId || c.workspaceId === workspaceId) c.res.write(msg);
  }
}

function broadcastGlobal(event, data) {
  const msg = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const c of clients) c.res.write(msg);
}

// ── Helpers ──────────────────────────────────────
function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    // Capture payloads carry base64 images, so the cap is generous — but it
    // exists, so a malformed stream can't grow until the process dies.
    const MAX = 128 * 1024 * 1024;
    req.on('data', chunk => {
      body += chunk;
      if (body.length > MAX) { body = ''; req.destroy(); resolve({}); }
    });
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve({}); }
    });
  });
}

function workspaceSummary(ws) {
  return {
    id: ws.id, projectName: ws.projectName, branch: ws.branch,
    mockupDir: ws.mockupDir, mockups: ws.knownFiles.size,
    sessions: ws.sessions.length, lastActive: ws.lastActive,
  };
}

let tailnetAddress = null;

// ── HTTP Server ──────────────────────────────────
// Read per request, not once at boot: this is a local tool that gets edited
// while it runs, and a cached template silently serves stale HTML until
// someone thinks to restart the server.
let templateCache = { mtime: 0, html: '' };
function loadTemplate() {
  try {
    const mtime = fs.statSync(HARNESS).mtimeMs;
    if (mtime !== templateCache.mtime) {
      templateCache = { mtime, html: fs.readFileSync(HARNESS, 'utf8') };
    }
  } catch {}
  return templateCache.html;
}
let browserOpened = false;

// The trust boundary: this server holds the owner's review state and can spawn
// tools, and it listens on localhost — which every web page the owner has open
// can reach. Only the harness's own origins may cross it. No Origin header
// (same-origin navigation, curl, scripts) is trusted; a foreign Origin gets no
// CORS approval, and any state-changing method from one is refused outright.
function trustedOrigin(origin) {
  if (!origin) return true;
  return /^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/iu.test(origin)
    || /^https?:\/\/[a-z0-9-]+\.localhost(:\d+)?$/iu.test(origin)     // portless
    || /^https?:\/\/100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+(:\d+)?$/u.test(origin); // tailnet CGNAT
}

const handler = async (req, res) => {
  lastActivity = Date.now();
  const url = new URL(req.url, `http://localhost:${PORT}`);

  const origin = req.headers.origin;
  if (trustedOrigin(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin || '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  } else if (req.method !== 'GET' && req.method !== 'OPTIONS') {
    // text/plain and form posts skip preflight, so denying CORS alone does
    // not stop a hostile page from WRITING — refuse the request itself.
    res.writeHead(403, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'forbidden-origin' }));
    return;
  }
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  // ── PWA: installable review app ───────────────
  // Added to the home screen this runs standalone, which removes the browser's
  // own chrome — the bar that was covering the design in the first place.
  if (req.method === 'GET' && url.pathname === '/manifest.webmanifest') {
    res.writeHead(200, { 'Content-Type': 'application/manifest+json' });
    res.end(JSON.stringify({
      name: 'Design Explorer', short_name: 'Designs',
      start_url: '/', scope: '/', display: 'standalone',
      background_color: '#f4f4f5', theme_color: '#1e1916',
      orientation: 'any',
      icons: [
        { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
        { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
      ],
    }));
    return;
  }
  if (req.method === 'GET' && url.pathname === '/icon.svg') {
    res.writeHead(200, { 'Content-Type': 'image/svg+xml', 'Cache-Control': 'max-age=86400' });
    res.end(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192">
<rect width="192" height="192" rx="42" fill="#1e1916"/>
<rect x="40" y="46" width="52" height="100" rx="9" fill="#f6f1ec"/>
<rect x="102" y="46" width="50" height="58" rx="9" fill="#8d8177"/>
<circle cx="127" cy="130" r="17" fill="#b4552d"/>
</svg>`);
    return;
  }
  if (req.method === 'GET' && url.pathname === '/favicon.ico') {
    res.writeHead(204, { 'Cache-Control': 'max-age=86400' });
    res.end();
    return;
  }
  if (req.method === 'GET' && VENDOR_FILES.has(url.pathname)) {
    const [file, contentType] = VENDOR_FILES.get(url.pathname);
    try {
      const bytes = fs.readFileSync(path.join(__dirname, 'vendor', file));
      res.writeHead(200, {
        'Content-Type': contentType,
        'Content-Length': bytes.length,
        'Cache-Control': 'public, max-age=31536000, immutable',
      });
      res.end(bytes);
    } catch {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Bundled browser dependency is missing');
    }
    return;
  }
  if (req.method === 'GET'
      && url.pathname.match(/^\/workspace\/[^/]+\/assets\/.+$/)) {
    const parts = url.pathname.split('/');
    const ws = workspaces.get(decodeURIComponent(parts[2]));
    const relativePath = decodeURIComponent(parts.slice(4).join('/'));
    const file = ws && workspaceAssetFile(ws, relativePath);
    if (!file) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Workspace asset not found');
      return;
    }
    const bytes = fs.readFileSync(file);
    res.writeHead(200, {
      'Content-Type': assetContentType(file),
      'Content-Length': bytes.length,
      'Cache-Control': 'no-cache',
    });
    res.end(bytes);
    return;
  }

  // ── Full-size mockup view ─────────────────────
  // One mockup as a plain standalone page at its natural width. On a phone
  // this is the zoom surface: the browser's own pinch and pan work on a real
  // page far better than any reimplementation inside the carousel.
  if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/view\/[^/]+$/)) {
    const parts = url.pathname.split('/');
    const ws = workspaces.get(decodeURIComponent(parts[2]));
    const file = decodeURIComponent(parts[4]) + '.html';
    const entry = ws && ws.knownFiles.get(file);
    if (!entry) { res.writeHead(404); res.end('Mockup not found'); return; }
    const scr = 'script';
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1440">
<title>${file.replace(/</g, '&lt;')}</title>
<style>*,*::before,*::after{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif}</style>
<${scr}>(function(){var w=console.warn;window.__deRestoreWarn=function(){console.warn=w;delete window.__deRestoreWarn};console.warn=function(){if(!String(arguments[0]||'').startsWith('cdn.tailwindcss.com should not be used'))w.apply(console,arguments)}})()</${scr}>
<${scr} src="/vendor/tailwindcss-3.4.17.js"></${scr}>
<${scr}>if(window.__deRestoreWarn)window.__deRestoreWarn()</${scr}>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<${scr} src="/vendor/lucide-0.468.0.js"></${scr}>
</head><body>
${rewriteWorkspaceAssetUrls(entry.html, ws.id)}
<${scr}>if(window.lucide)try{lucide.createIcons()}catch(e){}</${scr}>
</body></html>`);
    return;
  }

  // ── Page ──────────────────────────────────────
  if (req.method === 'GET' && url.pathname === '/') {
    const page = loadTemplate();
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(page);

  // ── SSE ───────────────────────────────────────
  } else if (req.method === 'GET' && url.pathname === '/events') {
    const wsId = url.searchParams.get('workspace');
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    });

    // Send workspace list
    res.write(`event: workspaces\ndata: ${JSON.stringify(
      [...workspaces.values()].map(workspaceSummary)
    )}\n\n`);

    // Send existing mockups + sessions for relevant workspaces
    for (const [id, ws] of workspaces) {
      if (wsId && wsId !== id) continue;
      for (const [file, data] of ws.knownFiles) {
        res.write(`event: add\ndata: ${JSON.stringify({
          id: file.replace('.html', ''), html: rewriteWorkspaceAssetUrls(data.html, id),
          session: data.session, workspace: id,
        })}\n\n`);
      }
      for (const session of ws.sessions) {
        res.write(`event: session\ndata: ${JSON.stringify({ ...session, workspace: id })}\n\n`);
      }
    }

    res.write(`event: init-complete\ndata: {}\n\n`);

    const client = { res, workspaceId: wsId || null };
    clients.push(client);
    req.on('close', () => {
      const idx = clients.indexOf(client);
      if (idx >= 0) clients.splice(idx, 1);
    });

  // ── Register workspace ────────────────────────
  } else if (req.method === 'POST' && url.pathname === '/workspace/register') {
    const body = await readBody(req);
    if (!body.projectPath || !body.mockupDir) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'projectPath and mockupDir required' }));
      return;
    }
    let ws;
    try {
      ws = createWorkspace(body.projectPath, body.branch, body.mockupDir);
    } catch (error) {
      if (!error.code || !String(error.code).startsWith('workspace-')) throw error;
      res.writeHead(409, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: error.code,
        note: error.message,
        ...(error.currentMockupDir ? { currentMockupDir: error.currentMockupDir } : {}),
        ...(error.requestedMockupDir ? { requestedMockupDir: error.requestedMockupDir } : {}),
      }));
      return;
    }

    if (!browserOpened && !NO_OPEN) {
      browserOpened = true;
      if (process.platform === 'darwin') exec(`open http://localhost:${PORT}`);
      else if (process.platform === 'linux') exec(`xdg-open http://localhost:${PORT} 2>/dev/null`);
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(workspaceSummary(ws)));

  // ── Deregister workspace ──────────────────────
  } else if (req.method === 'DELETE' && url.pathname.startsWith('/workspace/')) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    removeWorkspace(id);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));

  // ── Batch start (suppress auto-session during writes) ──
  } else if (req.method === 'POST' && url.pathname.match(/^\/workspace\/[^/]+\/batch\/start$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end('Workspace not found'); return; }
    ws.batching = true;
    ws.lastActive = Date.now();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ batching: true }));

  // ── Batch end (create session immediately with all unassigned mockups) ──
  } else if (req.method === 'POST' && url.pathname.match(/^\/workspace\/[^/]+\/batch\/end$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end('Workspace not found'); return; }
    ws.batching = false;
    ws.lastActive = Date.now();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));

  // ── Create session (scoped to workspace) ──────
  } else if (req.method === 'POST' && url.pathname.match(/^\/workspace\/[^/]+\/session$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end('Workspace not found'); return; }
    const session = getOrCreateOpenSession(ws);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(session || {}));

  // ── Review-round config (ballot mode) ─────────
  // The agent writes round.json into the mockup dir to switch the reviewer's
  // UI into ballot mode; answering renames it so the round runs exactly once.
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/round$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    if (!ws) { res.end('{"mode":"explore"}'); return; }
    try {
      res.end(fs.readFileSync(path.join(ws.mockupDir, 'round.json'), 'utf8'));
    } catch { res.end('{"mode":"explore"}'); }

  // ── Signals: the append-only review log for this workspace ──
  // Raw jsonl so an agent can tail it, and an empty body when nothing has
  // been answered yet rather than a 404 the caller has to special case.
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/signals$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
    if (!ws) { res.end(''); return; }
    try {
      res.end(fs.readFileSync(path.join(ws.mockupDir, 'signals.jsonl'), 'utf8'));
    } catch { res.end(''); }

  // ── Review lock: written on ballot submit, cleared only by explicit unlock ──
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/lock$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    if (!ws) { res.end('null'); return; }
    try {
      res.end(fs.readFileSync(path.join(ws.mockupDir, 'review.lock'), 'utf8'));
    } catch { res.end('null'); }
  } else if (req.method === 'POST' && url.pathname.match(/^\/workspace\/[^/]+\/unlock$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end(); return; }
    const lockPath = path.join(ws.mockupDir, 'review.lock');
    let ok = false;
    try {
      fs.rmSync(lockPath, { force: true });
      ok = !fs.existsSync(lockPath);
    } catch {}
    res.writeHead(ok ? 200 : 500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(ok ? { ok: true } : { ok: false, error: 'unlock-failed' }));

  // ── Presentation manifest: guided walkthrough with highlights + feedback gates ──
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/presentation$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
    if (!ws) { res.end('null'); return; }
    try {
      res.end(fs.readFileSync(path.join(ws.mockupDir, 'presentation.json'), 'utf8'));
    } catch { res.end('null'); }

  // ── Presentation VO: one optional mp3 per mockup, living in <dir>/audio/ ──
  // 204 when a slide has no narration; the harness treats that as a silent
  // slide without filling the browser console with expected 404 errors.
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/audio\/[^/]+$/)) {
    const parts = url.pathname.split('/');
    const id = decodeURIComponent(parts[2]);
    const mockupId = decodeURIComponent(parts[4]).replace(/[^a-zA-Z0-9_-]/g, '');
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end(); return; }
    const audioPath = path.join(ws.mockupDir, 'audio', mockupId + '.mp3');
    try {
      const bytes = fs.readFileSync(audioPath);
      // Media elements need explicit length and range support to buffer —
      // headerless chunked audio stalls Chrome's player at readyState 0.
      const range = req.headers.range && /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if (range && (range[1] || range[2])) {
        const start = range[1] ? parseInt(range[1], 10) : 0;
        const end = range[2] ? Math.min(parseInt(range[2], 10), bytes.length - 1) : bytes.length - 1;
        res.writeHead(206, {
          'Content-Type': 'audio/mpeg',
          'Content-Length': end - start + 1,
          'Content-Range': `bytes ${start}-${end}/${bytes.length}`,
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'no-cache',
        });
        res.end(bytes.subarray(start, end + 1));
      } else {
        res.writeHead(200, {
          'Content-Type': 'audio/mpeg',
          'Content-Length': bytes.length,
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'no-cache',
        });
        res.end(bytes);
      }
    } catch {
      res.writeHead(204, { 'X-Design-Explorer-Audio': 'missing', 'Cache-Control': 'no-cache' });
      res.end();
    }

  // ── Submit feedback (write to file) ───────────
  } else if (req.method === 'POST' && url.pathname.match(/^\/workspace\/[^/]+\/feedback$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end('Workspace not found'); return; }
    const body = await readBody(req);
    const feedbackPath = path.join(ws.mockupDir, 'feedback.md');
    const lockPath = path.join(ws.mockupDir, 'review.lock');
    const archiveDir = path.join(ws.mockupDir, 'archive');
    const hasBallot = Array.isArray(body.ballot) && body.ballot.length > 0;
    const annotations = Array.isArray(body.annotations) ? body.annotations : [];
    const bCaptures = body.captures && typeof body.captures === 'object' ? body.captures : {};
    const bImages = body.images && typeof body.images === 'object' ? body.images : {};
    const content = typeof body.content === 'string' ? body.content : '';
    const meaningful = content.split('\n').some(l => l.trim() && !l.trim().startsWith('#'));
    const recordable = hasBallot || meaningful || annotations.length
      || Object.keys(bCaptures).length || Object.keys(bImages).length;
    // A locked workspace answers 409 instead of silently absorbing a re-review.
    // The harness offers Unlock; non-harness callers must pass literal
    // override:true — "false", 1, and other truthy strings do not count.
    if (recordable && fs.existsSync(lockPath) && body.override !== true) {
      res.writeHead(409, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'locked',
        note: 'review.lock present — unlock first or pass override:true' }));
      return;
    }
    const validatedImages = new Map();
    const rejectSpatialPayload = (error) => {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error }));
    };
    const isPlainContainer = (value) => value !== null
      && typeof value === 'object' && !Array.isArray(value);
    if (body.annotations != null && !Array.isArray(body.annotations)) {
      rejectSpatialPayload('invalid-annotations-payload: annotations must be an array');
      return;
    }
    if (body.captures != null && !isPlainContainer(body.captures)) {
      rejectSpatialPayload('invalid-capture-payload: captures must be an object of mockupId → html string');
      return;
    }
    if (body.images != null && !isPlainContainer(body.images)) {
      rejectSpatialPayload('invalid-image-payload: images must be an object of mockupId → data URL');
      return;
    }
    // Validate the complete spatial payload before a guard, archive, ballot,
    // lock, signal, feedback, or canonical artifact can be written. Silently
    // dropping malformed values would turn a bad request into an empty snapshot.
    for (const [captureId, value] of Object.entries(bCaptures)) {
      if (typeof value !== 'string') {
        rejectSpatialPayload(`invalid-capture-payload: captures[${JSON.stringify(captureId)}] must be a string`);
        return;
      }
    }
    for (const [captureId, value] of Object.entries(bImages)) {
      if (typeof value !== 'string') {
        rejectSpatialPayload(`invalid-image-payload: images[${JSON.stringify(captureId)}] must be a valid PNG/JPEG base64 data URL`);
        return;
      }
      const match = /^data:image\/(png|jpeg);base64,([A-Za-z0-9+/]+={0,2})$/u.exec(value);
      if (!match) {
        rejectSpatialPayload(`invalid-image-payload: images[${JSON.stringify(captureId)}] must be a valid PNG/JPEG base64 data URL`);
        return;
      }
      const unpadded = match[2].replace(/=+$/u, '');
      if (unpadded.length % 4 === 1) {
        rejectSpatialPayload(`invalid-image-payload: images[${JSON.stringify(captureId)}] contains malformed base64`);
        return;
      }
      const normalized = unpadded + '='.repeat((4 - (unpadded.length % 4)) % 4);
      if ((match[2].includes('=') && match[2] !== normalized)
          || Buffer.from(unpadded, 'base64').toString('base64') !== normalized) {
        rejectSpatialPayload(`invalid-image-payload: images[${JSON.stringify(captureId)}] contains malformed base64`);
        return;
      }
      validatedImages.set(captureId, {
        extension: match[1] === 'png' ? '.png' : '.jpg',
        bytes: Buffer.from(unpadded, 'base64'),
      });
    }
    const safeCaptureName = (captureId) => String(captureId).replace(/[^a-zA-Z0-9._-]/g, '_');
    // Distinct mockup ids must never collapse to the same on-disk capture stem.
    // Permit one id to carry both its HTML and image; reject different ids
    // before ballot, annotation, or capture writes can partially land.
    const captureNames = new Map();
    for (const captureId of [...Object.keys(bCaptures), ...Object.keys(bImages)]) {
      const safe = safeCaptureName(captureId);
      const prior = captureNames.get(safe);
      if (prior !== undefined && prior !== captureId) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          error: `capture-key-collision: "${prior}" and "${captureId}" both sanitize to "${safe}"`,
        }));
        return;
      }
      captureNames.set(safe, captureId);
    }
    // A submit carrying nothing below its header and nothing structured must
    // not clobber a real record — that exact loss happened once (tour-portal,
    // 2026-08-01: an empty submit blanked a 3-pick round's feedback.md).
    if (!recordable) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ path: feedbackPath, skipped: 'nothing to record' }));
      return;
    }
    const stamp = () => new Date().toISOString().replace(/[:.]/g, '-');
    const warnings = [];
    // Copy an existing artifact into archive/ before anything replaces it.
    // A retry may re-derive the same name after a later submit step failed;
    // accept EEXIST only when a regular nonsymlink destination already holds
    // exactly the source bytes. Every other collision or comparison error
    // fails closed without overwriting immutable archive history.
    const archive = (from, name) => {
      const to = path.join(archiveDir, name);
      try {
        if (!fs.existsSync(from)) return true;
        fs.mkdirSync(archiveDir, { recursive: true });
        fs.copyFileSync(from, to, fs.constants.COPYFILE_EXCL);
        return true;
      } catch (e) {
        if (!e || e.code !== 'EEXIST') return false;
        try {
          const destination = fs.lstatSync(to);
          if (!destination.isFile() || destination.isSymbolicLink()) return false;
          const bytes = fs.readFileSync(from);
          return bytes.length === destination.size && bytes.equals(fs.readFileSync(to));
        } catch { return false; }
      }
    };
    const spatialGuardPath = path.join(ws.mockupDir, 'spatial-artifacts.stale.json');
    const capturesDir = path.join(ws.mockupDir, 'captures');
    const canonicalCaptureExtensions = new Set(['.html', '.png', '.jpg']);
    let spatialState = null;
    let spatialSnapshotComplete = false;
    let feedbackLanded = !(meaningful || hasBallot);

    // A feedback POST is a complete spatial snapshot, including an empty one.
    // The stale guard is established before the first durable review write so
    // an interrupted or degraded transition can never present an older root
    // annotations.json/captures set as though it belongs to the newer review.
    const inspectCanonicalSpatial = () => {
      const retained = [];
      const files = [];
      const invalid = [];
      const inspectFile = (file, relative, kind) => {
        let stat;
        try {
          stat = fs.lstatSync(file);
        } catch (e) {
          if (e && e.code === 'ENOENT') return;
          throw e;
        }
        retained.push(relative);
        if (!stat.isFile() || stat.isSymbolicLink()) {
          invalid.push(relative);
          return;
        }
        files.push({ file, relative, kind });
      };

      inspectFile(path.join(ws.mockupDir, 'annotations.json'), 'annotations.json', 'annotations');
      let captureDirStat = null;
      try {
        captureDirStat = fs.lstatSync(capturesDir);
      } catch (e) {
        if (!e || e.code !== 'ENOENT') throw e;
      }
      if (captureDirStat) {
        if (!captureDirStat.isDirectory() || captureDirStat.isSymbolicLink()) {
          retained.push('captures/');
          invalid.push('captures/');
        } else {
          for (const name of fs.readdirSync(capturesDir)) {
            const file = path.join(capturesDir, name);
            const relative = `captures/${name}`;
            const stat = fs.lstatSync(file);
            // Unsupported regular files are outside the canonical capture set
            // and remain untouched. Any nonregular entry or symlink is unsafe
            // regardless of its name: never follow or recursively remove it.
            if (!stat.isFile() || stat.isSymbolicLink()) {
              retained.push(relative);
              invalid.push(relative);
              continue;
            }
            if (!canonicalCaptureExtensions.has(path.extname(name).toLowerCase())) continue;
            retained.push(relative);
            files.push({ file, relative, kind: 'capture' });
          }
        }
      }
      retained.sort();
      files.sort((a, b) => a.relative.localeCompare(b.relative));
      invalid.sort();
      return { retained, files, invalid };
    };

    const establishSpatialGuard = () => {
      let tempPath = null;
      let fd = null;
      try {
        const state = inspectCanonicalSpatial();
        tempPath = `${spatialGuardPath}.${process.pid}.${crypto.randomUUID()}.tmp`;
        fd = fs.openSync(tempPath, 'wx', 0o600);
        fs.writeFileSync(fd, JSON.stringify({
          schema: 'design-explorer.spatial-artifacts-stale.v1',
          workspace: ws.id,
          staleAt: new Date().toISOString(),
          reason: 'a newer review attempt is replacing the canonical spatial snapshot until the transition completes',
          retained: state.retained,
        }, null, 2) + '\n');
        fs.fsyncSync(fd);
        fs.closeSync(fd);
        fd = null;
        fs.renameSync(tempPath, spatialGuardPath);
        tempPath = null;
        return state;
      } catch (e) {
        if (fd !== null) {
          try { fs.closeSync(fd); } catch {}
        }
        if (tempPath) {
          try { fs.unlinkSync(tempPath); } catch {}
        }
        throw new Error(`spatial-stale-stamp-failed: ${e.message}`);
      }
    };

    const commitSpatialSnapshot = (state) => {
      try {
        if (state.invalid.length) {
          warnings.push('spatial-artifacts-stale: nonregular or symlink canonical spatial member(s) retained: '
            + state.invalid.join(', '));
          return false;
        }

        // Archive the WHOLE prior canonical set before deleting or overwriting
        // any member. A partial archive leaves every original in place.
        const archiveFailures = [];
        for (const entry of state.files) {
          try {
            const current = fs.lstatSync(entry.file);
            if (!current.isFile() || current.isSymbolicLink()) {
              archiveFailures.push(entry.relative);
              continue;
            }
            const prevTs = current.mtime.toISOString().replace(/[:.]/g, '-');
            const ext = path.extname(entry.file);
            const stem = path.basename(entry.file, ext);
            const archiveName = entry.kind === 'annotations'
              ? `annotations-${prevTs}.json`
              : `capture-${stem}-${prevTs}${ext}`;
            if (!archive(entry.file, archiveName)) archiveFailures.push(entry.relative);
          } catch {
            archiveFailures.push(entry.relative);
          }
        }
        if (archiveFailures.length) {
          warnings.push('spatial-artifacts-stale: archive failed; prior canonical spatial artifacts retained: '
            + archiveFailures.join(', '));
          return false;
        }

        // Every old byte is now recoverable from archive/. Clear all canonical
        // members, including ids omitted by this request, before writing the new
        // complete snapshot.
        try {
          for (const entry of state.files) fs.unlinkSync(entry.file);
          if (fs.existsSync(capturesDir)
              && fs.lstatSync(capturesDir).isDirectory()
              && fs.readdirSync(capturesDir).length === 0) {
            fs.rmdirSync(capturesDir);
          }
        } catch (e) {
          warnings.push(`spatial-artifacts-stale: clear failed after archival; archived bytes remain recoverable: ${e.message}`);
          return false;
        }

        try {
          if (annotations.length) {
            fs.writeFileSync(
              path.join(ws.mockupDir, 'annotations.json'),
              JSON.stringify({
                schema: 'design-explorer.annotations.v1',
                workspace: ws.id,
                round: ws.openSessionId,
                submittedAt: new Date().toISOString(),
                note: 'pin.target.anchor and markup.points are percentages of the page box',
                mockups: annotations,
              }, null, 2),
            );
          }

          const writes = [];
          for (const id of Object.keys(bCaptures)) {
            writes.push({
              file: path.join(capturesDir, safeCaptureName(id) + '.html'),
              bytes: bCaptures[id],
            });
          }
          for (const [id, image] of validatedImages) {
            writes.push({
              file: path.join(capturesDir, safeCaptureName(id) + image.extension),
              bytes: image.bytes,
            });
          }
          if (writes.length) fs.mkdirSync(capturesDir, { recursive: true });
          for (const write of writes) fs.writeFileSync(write.file, write.bytes);
          return true;
        } catch (e) {
          warnings.push(`spatial-artifacts-stale: new spatial snapshot write failed; archived prior bytes remain recoverable: ${e.message}`);
          return false;
        }
      } catch (e) {
        warnings.push(`spatial-artifacts-stale: spatial snapshot transition failed closed: ${e.message}`);
        return false;
      }
    };
    try {
      if (!hasBallot) spatialState = establishSpatialGuard();
      // Ballot first, feedback.md LAST: the ballot is the signal, and ordering
      // the writes this way means a throw mid-handler can never leave the
      // reviewer with a destroyed record and a 500.
      if (hasBallot) {
        const round = readRound(ws);
        let entries = body.ballot
          .filter(entry => entry && typeof entry === 'object')
          .map((entry, index) => {
            const matchup = matchupFor(round, entry, index);
            return { picked: normalizeBallotEntry(entry, matchup), matchup };
          });
        // A re-answer replaces the earlier answer; two entries for one question
        // in a single batch would otherwise mint colliding lineIds.
        entries = [...new Map(entries.map(e => [e.picked.question, e])).values()];
        // Validate BEFORE any write. A ballot that fails here changes nothing:
        // no lock, no signals, no retirement — the round stays live.
        const reject = (why) => {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: why }));
        };
        if (!entries.length) { reject('empty-ballot: no valid entries'); return; }
        if (round && Array.isArray(round.matchups)
            && entries.length < round.matchups.length) {
          reject(`incomplete-ballot: ${entries.length} answer(s) for `
            + `${round.matchups.length} matchup(s) — finish the round first`);
          return;
        }
        if (round && Array.isArray(round.matchups)
            && (entries.length > round.matchups.length
              || entries.some(({ picked, matchup }) => !matchup
                || picked.question !== matchup.question))) {
          reject('unexpected-ballot: answers must map one-to-one to the live round matchups');
          return;
        }
        for (const { picked, matchup } of entries) {
          const ids = optionIdsFor(matchup, picked);
          if (picked.neither) {
            // A Neither without its why-not is dead signal, and one without an
            // option set marks nothing a loser. The harness enforces both; the
            // server must too, or any other caller can starve the funnel.
            // The always-offered "other" chip names no reason — alone it does
            // not count as a why.
            const substantive = picked.reasons.filter(r =>
              String(r).trim().toLowerCase() !== 'other');
            if (!picked.note && !substantive.length) {
              reject(`neither-needs-why: "${picked.question}" rejected every option with no actionable reason or note`);
              return;
            }
            if (!ids.length) {
              reject(`neither-needs-options: "${picked.question}" carries no optionIds and matches no round matchup`);
              return;
            }
          } else if (picked.mode === 'rank') {
            const unique = new Set(picked.order);
            if (!picked.order.length || unique.size !== picked.order.length
                || (ids.length && (picked.order.length !== ids.length
                  || picked.order.some(id => !ids.includes(id))))) {
              reject(`invalid-order: "${picked.question}" must rank every option exactly once`);
              return;
            }
          } else if (matchup && ids.length) {
            if (!ids.includes(picked.winnerId)) {
              reject(`invalid-winner: "${picked.winnerId}" is not an option of "${picked.question}"`);
              return;
            }
          }
        }
        try {
          if (fs.existsSync(lockPath)) {
            if (!fs.lstatSync(lockPath).isFile()) {
              throw new Error('review.lock is not a regular file');
            }
            fs.accessSync(lockPath, fs.constants.W_OK);
          } else {
            fs.accessSync(ws.mockupDir, fs.constants.W_OK);
          }
        } catch (e) {
          throw new Error(`lock-preflight-failed: ${e.message}`);
        }
        const ballotPath = path.join(ws.mockupDir, 'ballot.json');
        // Never destroy an earlier round's answers: archive the old ballot
        // FAIL-CLOSED — if the copy cannot be made, the whole submit aborts
        // before anything is replaced. If the old ballot predates signals.jsonl
        // (the v1 era, including a zero-byte file), replay its picks with the
        // answered round's matchups so the original topology survives.
        if (fs.existsSync(ballotPath)) {
          const old = JSON.parse(fs.readFileSync(ballotPath, 'utf8'));
          if (!archive(ballotPath,
              `ballot-${String(old.submittedAt || 'undated').replace(/[:.]/g, '-')}.json`)) {
            throw new Error('archive-failed: refusing to overwrite ballot.json without a copy');
          }
          try {
            const sigPath = path.join(ws.mockupDir, 'signals.jsonl');
            const sigEmpty = !fs.existsSync(sigPath)
              || fs.readFileSync(sigPath, 'utf8').trim().length === 0;
            if (sigEmpty && Array.isArray(old.picks)) {
              // Whitespace carries no append-only record and would otherwise
              // remain an unreadable JSONL line ahead of the migrated signal.
              if (fs.existsSync(sigPath) && fs.statSync(sigPath).size > 0) {
                fs.writeFileSync(sigPath, '');
              }
              let answered = null;
              try {
                answered = JSON.parse(fs.readFileSync(
                  path.join(ws.mockupDir, 'round.answered.json'), 'utf8'));
              } catch {}
              appendSignals(ws,
                old.picks.map((p, i) => {
                  const m = matchupFor(answered, p, i);
                  return { picked: normalizeBallotEntry(p, m), matchup: m };
                }),
                { migratedFrom: old.schema || 'ballot.v1' });
            }
          } catch {}
        }
        // Old-ballot archival/migration preserves the still-current review and
        // may fail independently. Establish the stale guard only at the last
        // precommit seam, immediately before the new ballot replaces it.
        spatialState = establishSpatialGuard();
        fs.writeFileSync(
          ballotPath,
          JSON.stringify({
            schema: 'design-explorer.ballot.v2',
            workspace: ws.id,
            submittedAt: new Date().toISOString(),
            picks: entries.map(e => e.picked),
          }, null, 2),
        );
        const appended = appendSignals(ws, entries);
        if (appended && appended.workspace === false) warnings.push('signals-append-failed: workspace signals.jsonl was not written');
        // A submitted ballot locks the workspace against accidental re-review;
        // only the explicit unlock route clears it.
        fs.writeFileSync(lockPath, JSON.stringify({
          submittedAt: new Date().toISOString(),
          picks: entries.length,
        }, null, 2));
        // Retire the round without eating history: every answered round lands
        // in archive/ under its own name; round.answered.json stays "latest".
        // If the archive copy fails the round is NOT retired — better to risk
        // a duplicate ballot than to destroy the only copy of the questions.
        try {
          const roundPath = path.join(ws.mockupDir, 'round.json');
          if (fs.existsSync(roundPath)) {
            if (archive(roundPath, `round-${stamp()}.answered.json`)) {
              fs.copyFileSync(roundPath, path.join(ws.mockupDir, 'round.answered.json'));
              fs.unlinkSync(roundPath);
            } else {
              warnings.push('round-not-retired: archive copy failed, round.json kept in place');
            }
          } else {
            // Presentation-driven ballots have no round.json — snapshot the
            // deck so its questions survive the next round's rewrite.
            const presoPath = path.join(ws.mockupDir, 'presentation.json');
            if (fs.existsSync(presoPath)) {
              if (!archive(presoPath, `presentation-${stamp()}.answered.json`)) {
                warnings.push('presentation-not-archived: archive copy failed, presentation.json kept in place');
              }
            }
          }
        } catch {}
      }

      // Structured markup + page captures are one complete spatial snapshot.
      // Once a ballot has landed, any degraded transition is a 200 + warning:
      // the durable stale guard tells readers not to consume partial/root data.
      spatialSnapshotComplete = commitSpatialSnapshot(spatialState);
      // Human-readable record LAST, and never over a live prior round: the
      // old file is archived under its own mtime FAIL-CLOSED — if the copy
      // cannot be made, the old record stays and the new text is reported as
      // preserved-not-written rather than silently clobbering it.
      if (meaningful || hasBallot) {
        let priorSafe = true;
        try {
          if (fs.existsSync(feedbackPath)
              && fs.readFileSync(feedbackPath, 'utf8').trim()) {
            const prevTs = fs.statSync(feedbackPath).mtime.toISOString().replace(/[:.]/g, '-');
            priorSafe = archive(feedbackPath, `feedback-${prevTs}.md`);
          }
        } catch { priorSafe = false; }
        if (priorSafe) {
          fs.writeFileSync(feedbackPath, content);
          feedbackLanded = true;
        } else {
          warnings.push('feedback-preserved: archive copy failed, prior feedback.md kept, new text NOT written');
        }
      }

      // Remove the guard only after the complete spatial snapshot and its
      // applicable feedback record have landed. Failure is conservative: the
      // new files stay recoverable but are not advertised as current.
      if (spatialSnapshotComplete && feedbackLanded) {
        try {
          fs.unlinkSync(spatialGuardPath);
        } catch (e) {
          if (!e || e.code !== 'ENOENT') {
            warnings.push(`spatial-artifacts-stale: snapshot landed but stale guard removal failed: ${e.message}`);
          }
        }
      }

      // Close current session — next files start a new round
      if (ws.openSessionId !== null) {
        const session = ws.sessions.find(s => s.id === ws.openSessionId);
        if (session) {
          session.closed = true;
          saveSessions(ws);
          broadcastToWorkspace(ws.id, 'session-closed', { id: session.id, workspace: ws.id });
        }
        ws.openSessionId = null;
      }
      ws.lastActive = Date.now();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(warnings.length
        ? { path: feedbackPath, warnings }
        : { path: feedbackPath }));
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }

  // ── Context: gather workspace context for the reviewing agent ───
  } else if (req.method === 'GET' && url.pathname.match(/^\/workspace\/[^/]+\/context$/)) {
    const id = decodeURIComponent(url.pathname.split('/')[2]);
    const ws = workspaces.get(id);
    if (!ws) { res.writeHead(404); res.end('Workspace not found'); return; }

    const mockupList = [];
    for (const [file, data] of ws.knownFiles) {
      mockupList.push({
        id: file.replace('.html', ''),
        filename: file,
        session: data.session,
        html: data.html,
      });
    }

    const context = {
      workspace: {
        id: ws.id,
        projectPath: ws.projectPath,
        projectName: ws.projectName,
        branch: ws.branch,
        mockupDir: ws.mockupDir,
      },
      mockups: mockupList,
      sessions: ws.sessions,
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(context));

  // ── Health check ──────────────────────────────
  } else if (req.method === 'GET' && url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      protocol: PROTOCOL,
      pid: process.pid,
      port: PORT,
      tailnet: tailnetAddress,
      workspaces: [...workspaces.values()].map(workspaceSummary),
    }));

  // ── List workspaces ───────────────────────────
  } else if (req.method === 'GET' && url.pathname === '/workspaces') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify([...workspaces.values()].map(workspaceSummary)));

  // ── Legacy compat: POST /session ──────────────
  } else if (req.method === 'POST' && url.pathname === '/session') {
    const ws = [...workspaces.values()][0];
    if (!ws) { res.writeHead(404); res.end('No workspaces'); return; }
    const session = getOrCreateOpenSession(ws);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(session || {}));

  } else {
    res.writeHead(404);
    res.end('Not found');
  }
};

const server = http.createServer(handler);

// SECURITY: bind loopback only. The optional tailnet listener is still
// unauthenticated, so it must never widen to the LAN.
/**
 * Loopback is always the primary listener. `--tailnet` adds a SECOND listener
 * bound to this machine's Tailscale address only — reachable from your own
 * devices, still invisible to whatever LAN you are sitting on. We never bind
 * 0.0.0.0 because review and feedback endpoints are not authenticated.
 */
function tailscaleIP() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const ni of nets[name] || []) {
      if (ni.family === 'IPv4' && !ni.internal && /^100\./.test(ni.address)) return ni.address;
    }
  }
  return null;
}

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n  Design Explorer (singleton) → http://localhost:${PORT}`);
  console.log(`  PID: ${process.pid}`);

  if (WANT_TAILNET) {
    const ip = tailscaleIP();
    if (!ip) {
      console.log('  Tailnet: ✗ no 100.x address found — is Tailscale up?\n');
    } else {
      const tsServer = http.createServer(handler);
      tsServer.on('error', (e) => console.log(`  Tailnet: ✗ ${e.message}\n`));
      tsServer.listen(PORT, ip, () => {
        tailnetAddress = `http://${ip}:${PORT}`;
        console.log(`  Tailnet: http://${ip}:${PORT}  (your devices only)\n`);
      });
    }
  } else {
    console.log('  Tailnet: off — pass --tailnet to review from your phone\n');
  }

  // Legacy mode: auto-register if --dir was passed
  if (LEGACY_DIR) {
    const dir = path.resolve(LEGACY_DIR);
    let branch = 'default';
    try { branch = require('child_process').execSync('git branch --show-current', { cwd: path.dirname(dir) }).toString().trim() || 'default'; } catch {}
    const projectPath = path.dirname(dir);
    createWorkspace(projectPath, branch, dir);
    console.log(`  Legacy mode: registered ${path.basename(projectPath)} (${branch})`);

    if (!NO_OPEN) {
      browserOpened = true;
      if (process.platform === 'darwin') exec(`open http://localhost:${PORT}`);
      else if (process.platform === 'linux') exec(`xdg-open http://localhost:${PORT} 2>/dev/null`);
    }
  }
});

// Idle shutdown: a registered workspace is configuration, not activity.
// Browser clients, requests, file changes, and feedback keep the server alive.
setInterval(() => {
  if (clients.length > 0) return;
  const workspaceActivity = Math.max(0, ...[...workspaces.values()].map(ws => ws.lastActive || 0));
  if (Date.now() - Math.max(lastActivity, workspaceActivity) > IDLE_TIMEOUT_MS) {
    console.log(`Idle shutdown (${Math.round(IDLE_TIMEOUT_MS / 60000)} min without activity)`);
    cleanup();
  }
}, IDLE_POLL_MS);
