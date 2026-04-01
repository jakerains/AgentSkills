# Platform Patterns

Use this reference when the host is Electron, Swift, Next.js, or another environment with platform-specific constraints.

## Electron

Preferred pattern: local desktop bridge over `stdio`.

- Spawn `codex app-server` in the Electron main process.
- Keep raw JSON-RPC, auth state, and approvals in the main process.
- Expose a narrow IPC surface through `contextBridge` or an equivalent preload layer.
- Open managed ChatGPT login in the system browser, not inside an untrusted renderer.

Why this works well:

- App Server's default transport is `stdio`.
- Managed ChatGPT login uses a localhost callback, which fits a local desktop app well.
- The renderer does not need direct access to tokens or the child process.

Use `assets/electron-main-process` as the starting point.

## Next.js Web Apps

Preferred pattern: server-side bridge or sidecar.

- Run `codex app-server` in a Node server context, worker, or sidecar.
- Keep all app-server communication on the server side.
- Convert app-server events into your own SSE, WebSocket, or route-level streaming protocol for the browser.
- Keep browser code unaware of raw app-server auth details whenever possible.

Important auth constraint:

- The documented managed `chatgpt` flow returns an `authUrl` that redirects back to a localhost callback served by app-server.
- That is a strong fit for local desktop apps.
- It is not a great default for a server-hosted browser app, because the callback terminates at the machine running app-server, not automatically at the end user's browser session.

Recommended auth strategy for web apps:

- Prefer host-managed `chatgptAuthTokens` if your product already owns ChatGPT auth.
- Otherwise, design a deliberate server-side auth bridge instead of assuming managed localhost auth will just work.

Use `assets/nextjs-web-sidecar` as the starting point.

## Swift Hosts

### macOS desktop apps

Preferred pattern: local process bridge.

- Use `Process` and `Pipe` to spawn and communicate with `codex app-server`.
- Keep JSON-RPC parsing and transport logic in a dedicated bridge object.
- Open managed ChatGPT login in the system browser.

This is the closest Swift equivalent to the Electron main-process pattern.

### iOS and constrained Apple platforms

Preferred pattern: sidecar or backend bridge.

- Do not assume the app can spawn a local `codex` binary.
- Use a WebSocket bridge to a local companion, a background helper, or your own server-side bridge instead.
- Favor externally managed `chatgptAuthTokens` or an app-owned auth layer when you need a user-specific session.

Use `assets/swift-bridge-patterns` as the starting point.

## Generic Decision Rules

### Use local `stdio`

Choose this when:

- the host can spawn child processes
- the host is desktop or developer-tool oriented
- the app-server instance should stay private to a single local session

Typical fits:

- Electron
- macOS Swift
- local Node tooling

### Use WebSocket or another server-side bridge

Choose this when:

- the UI is browser-first
- the host cannot safely spawn a local process
- the app-server instance needs to run behind another service boundary

Typical fits:

- Next.js web apps
- iOS or sandboxed mobile apps
- remote service architectures

## What to Avoid

- Do not embed raw app-server credentials or approval decisions directly into browser code.
- Do not expose a non-loopback WebSocket listener without explicit auth.
- Do not assume managed ChatGPT login is automatically suitable for every host, because the documented callback shape is localhost-oriented.
