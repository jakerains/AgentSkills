# Overview and Architecture

Use this reference when deciding whether App Server is the right integration surface and how to host it.

## What App Server Is

`codex app-server` is the rich-client protocol layer behind Codex interfaces such as the official VS Code extension. It is designed for products that need:

- OpenAI-managed or host-managed authentication
- stored conversation history
- approval prompts
- streamed agent events
- rich UI state around threads, turns, items, and review

If the user only needs to run Codex tasks in CI, background jobs, or non-interactive automation, prefer the Codex SDK instead.

## App Server vs Codex SDK

| Need | Prefer |
| --- | --- |
| Embedded chat-like client inside a product | App Server |
| Approval UX and streamed item events | App Server |
| Reusing a user's ChatGPT-backed access in a host app | App Server |
| CI jobs, server automation, background workers | Codex SDK |
| Direct protocol control and host-managed UI | App Server |

## Transport Choice

### `stdio` (default)

Use `stdio` first.

- It is the documented default.
- It is the simplest way to keep the app-server process private to the host app.
- It avoids WebSocket auth and remote exposure decisions.
- It fits desktop apps, local developer tools, Electron, and macOS Swift hosts well.

### `websocket` (experimental)

Use WebSocket when a child process is not a good fit or when the host needs a socket-based integration boundary.

- Treat it as experimental.
- For remote or non-loopback use, configure explicit WebSocket auth.
- Handle backpressure and retry on `-32001` with exponential backoff and jitter.
- This is often the cleaner fit for browser-first web apps, iOS, or other hosts that cannot directly own a local `codex` process.

From the open-source repo:

- loopback listeners are the safe default for local use
- non-loopback listeners should not be exposed without auth
- the supported auth flags are:
  - `--ws-auth capability-token --ws-token-file /absolute/path`
  - `--ws-auth signed-bearer-token --ws-shared-secret-file /absolute/path`

## Recommended Host Patterns

### Greenfield local client

Use a child process boundary.

- Spawn `codex app-server`
- speak JSON-RPC over stdio
- keep request state and UI state in the host app
- generate schemas from the local `codex` binary

Use `assets/node-stdio-starter` as the base.

### Electron desktop app

Use the main process as the trust boundary.

- spawn `codex app-server` in the main process
- keep approvals and auth state out of the renderer
- expose a small typed IPC API to the UI layer
- open managed ChatGPT login in the system browser

Use `assets/electron-main-process` as the base.

### Next.js web app

Use a server-side bridge.

- run app-server in a route handler, worker, or sidecar
- normalize item streams before sending them to the browser
- keep raw app-server transport and auth state on the server
- prefer externally managed ChatGPT tokens or another deliberate auth bridge for browser-first products

Use `assets/nextjs-web-sidecar` as the base.

### Swift host

Split by platform capabilities.

- macOS desktop: use `Process` plus pipes for a local bridge
- iOS or constrained hosts: use a WebSocket or backend bridge instead of local process spawning

Use `assets/swift-bridge-patterns` as the base.

### Existing app with its own auth or UI shell

Use a thin bridge layer.

- keep your app's routing, UI state, and auth orchestration
- wrap app-server requests behind a small client
- adapt server notifications into your existing event system
- treat approvals and token refresh as first-class UI events

Use `assets/existing-app-auth-bridge` as the base.

## Schema Strategy

Do not hand-maintain TypeScript request and response types.

Generate schemas from the same `codex` version you will run:

```bash
codex app-server generate-ts --out ./schemas/typescript
codex app-server generate-json-schema --out ./schemas/json-schema
```

The bundled `scripts/generate-schemas.sh` wraps this and creates both outputs.

## Initialization Constraints

Each connection must:

1. send `initialize`
2. wait for the result
3. send `initialized`

Requests sent before this handshake will fail with `Not initialized`.
Repeated `initialize` calls on the same connection will fail with `Already initialized`.

## Experimental Capability

Some methods and fields require:

```json
{
  "capabilities": {
    "experimentalApi": true
  }
}
```

If you use experimental methods or fields without opting in, app-server rejects them.

Use experimental features only when the request truly needs them, and document that choice in the host app.
