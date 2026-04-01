---
name: codex-app-server
description: Build rich Codex integrations with the Codex App Server across Electron, Swift, Next.js, and other host apps. Use when embedding Codex into a product, adding ChatGPT or API-key login to a desktop or web host, integrating managed or externally supplied ChatGPT tokens, streaming thread/turn/item events, handling approvals, generating version-matched schemas, or deciding between App Server and the Codex SDK for a new or existing app.
---

# Codex App Server

Embed Codex into a host product using the same protocol used by OpenAI's rich Codex clients. This skill is adaptable across Electron, Swift, Next.js, and other hosts by choosing the right transport and bridge pattern for each environment.

## Start Here

1. Decide whether the request needs App Server or the Codex SDK.
2. Re-check the official docs if the request depends on the latest auth or protocol behavior.
3. Pick the closest bundled starter from `assets/` for the target host.
4. Generate version-matched schemas with `scripts/generate-schemas.sh` before building a typed client.

## Choose the Right Surface

- Use App Server when the host product needs embedded authentication, conversation history, approvals, streamed agent events, review mode, rate limits, or a custom UI around threads and turns.
- Use the Codex SDK for automation, CI, server-side jobs, or non-interactive workflows.
- Prefer `stdio` first for local desktop hosts that can spawn `codex app-server`. Use WebSocket when the host cannot manage a child process, when the UI is browser-based, or when a separate sidecar/service boundary is the cleaner architecture.
- Treat WebSocket and `experimentalApi` features as opt-in. They are useful, but they are not the safest production default.
- Desktop hosts like Electron and macOS Swift apps can usually use managed ChatGPT login comfortably because the browser flow returns to a localhost callback owned by app-server.
- Browser-first web apps usually need a server-side bridge or host-managed tokens. The documented managed ChatGPT flow returns an `authUrl` with a localhost callback, which is a poor default fit for a pure browser deployment.

## Workflow

1. Generate schemas from the same `codex` version you will run:

```bash
./scripts/generate-schemas.sh ./schemas
```

2. Start from the right asset:
- `assets/node-stdio-starter` for a greenfield Node/TS client.
- `assets/existing-app-auth-bridge` for an existing app that already owns auth, routing, or UI state.
- `assets/electron-main-process` for Electron main/preload/renderer boundaries.
- `assets/nextjs-web-sidecar` for a Next.js server-side bridge that keeps app-server off the browser bundle.
- `assets/swift-bridge-patterns` for Swift desktop and sidecar-based WebSocket patterns.

3. Implement the initialize handshake:
- Open the transport.
- Send `initialize` with `clientInfo`.
- Wait for the response.
- Send `initialized`.
- Do not send other requests before this handshake completes.

4. Manage threads:
- `thread/start` for a new conversation.
- `thread/resume` to continue an existing thread.
- `thread/fork` when the user wants a branch of existing history.
- `thread/read` and `thread/list` for history views that should not resume execution.

5. Manage turns:
- `turn/start` to submit user input.
- `turn/steer` for follow-up input on an in-flight turn.
- `turn/interrupt` to cancel.
- Keep reading notifications until `turn/completed`.

6. Render item streams correctly:
- Treat `item/started` and `item/completed` as the authoritative item state.
- Append deltas for `agentMessage`, `reasoning`, `plan`, and command output in order.
- Model the UI around `Thread`, `Turn`, and `ThreadItem`, not just plain chat messages.

7. Implement approvals:
- Render server-initiated approval requests for command execution, file changes, and `tool/requestUserInput`.
- Scope approval UI by `threadId` and `turnId`.
- Default to the narrowest approval option unless the user explicitly wants broader session permissions.

8. Implement auth:
- Use `apiKey` mode when the host app wants OpenAI API-key auth.
- Use managed `chatgpt` mode when app-server should own browser login and token refresh.
- Use `chatgptAuthTokens` when the host app already owns ChatGPT auth and can supply fresh `idToken` and `accessToken`.
- If the server sends `account/chatgptAuthTokens/refresh`, respond quickly with fresh tokens or the original request will fail.

9. Surface account state:
- Use `account/read` to discover the active auth state.
- Use `account/updated` to update the UI.
- Use `account/rateLimits/read` and `account/rateLimits/updated` to show ChatGPT-backed usage state in-product.

10. Adapt the bridge to the host platform:
- Electron: spawn app-server in the main process, expose a narrow IPC surface to the renderer, and open managed ChatGPT login in the system browser.
- Next.js web app: run app-server in a server-side route handler, worker, or sidecar process; normalize streamed events before sending them to the browser; avoid shipping raw app-server credentials or transports to client-side code.
- Swift macOS app: use `Process` for a local app-server bridge when the app can ship or locate the `codex` binary.
- Swift iOS or constrained environments: use a WebSocket sidecar or your own backend bridge; do not assume the app can spawn a local `codex` process.

## Auth Guidance

- "Let users use their Codex or ChatGPT subscription in our app" maps to ChatGPT auth modes plus the account and rate-limit endpoints.
- Managed ChatGPT login returns an `authUrl`; the host should open it in the system browser and wait for `account/login/completed`.
- Managed ChatGPT login is best for local desktop hosts because the documented auth flow uses a localhost callback served by app-server itself.
- For browser-first web apps, prefer host-managed `chatgptAuthTokens` or a carefully designed bridge. Do not assume a server-hosted app-server can complete a localhost callback in the end user's browser.
- External-token mode is best when your app already authenticates the user with ChatGPT and can refresh tokens itself.
- `requiresOpenaiAuth` tells you whether the active provider requires OpenAI credentials before Codex can run.
- Do not promise undocumented subscription-management APIs. The documented surface is auth, account state, plan type, and rate-limit oriented.

## References

- Architecture, transport, and surface choice: `references/overview-and-architecture.md`
- Platform-specific host patterns: `references/platform-patterns.md`
- Auth flows, rate limits, and token refresh: `references/auth-and-account-flows.md`
- JSON-RPC protocol, lifecycle, events, and approvals: `references/protocol-and-events.md`

## Execution Rules

- Prefer official OpenAI docs and the open-source `openai/codex` app-server implementation over third-party examples.
- Generate schemas from the local `codex` binary instead of hand-maintaining request types.
- Prefer `stdio` unless there is a concrete reason to expose WebSocket transport.
- Match the integration pattern to the host platform instead of forcing one transport everywhere.
- Warn when the request assumes undocumented subscription APIs.
- Keep production integrations resilient to backpressure, reconnects, `Not initialized`, `Already initialized`, and approval interruptions.
- For WebSocket transport, document the current auth mode and remote exposure risks before recommending it.
