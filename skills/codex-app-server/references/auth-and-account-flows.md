# Auth and Account Flows

Use this reference when the request involves login, account state, ChatGPT-backed access, token refresh, or rate limits.

## Auth Modes

App Server supports three auth modes.

| Mode | Use when | Host responsibility |
| --- | --- | --- |
| `apiKey` | The app wants OpenAI API-key auth | Collect and store the API key |
| `chatgpt` | App Server should own the ChatGPT browser flow and token refresh | Open the returned `authUrl` and wait for notifications |
| `chatgptAuthTokens` | The host app already owns ChatGPT auth | Supply `idToken` and `accessToken`, and refresh them on request |

## Check Current Auth State

Use `account/read` first:

```json
{ "method": "account/read", "id": 1, "params": { "refreshToken": false } }
```

Important fields:

- `account`: current account state, or `null`
- `requiresOpenaiAuth`: whether the active provider requires OpenAI credentials

Managed ChatGPT mode can also return fields such as:

- `email`
- `planType`

Treat these as display state, not as a subscription-management API.

## API Key Login

Send:

```json
{
  "method": "account/login/start",
  "id": 2,
  "params": { "type": "apiKey", "apiKey": "sk-..." }
}
```

Then expect:

- immediate success response
- `account/login/completed`
- `account/updated` with `authMode: "apikey"`

## Managed ChatGPT Login

Send:

```json
{ "method": "account/login/start", "id": 3, "params": { "type": "chatgpt" } }
```

The result includes:

- `loginId`
- `authUrl`

Recommended host flow:

1. open `authUrl` in the system browser
2. show a waiting state in the app
3. wait for `account/login/completed`
4. update UI again when `account/updated` arrives

The server hosts the local callback during this flow.

This makes managed ChatGPT login a natural fit for local desktop hosts such as Electron and macOS Swift apps. It is a weaker default fit for pure browser deployments because the callback terminates at the machine running app-server.

## Externally Managed ChatGPT Tokens

Use this mode when the host app already owns ChatGPT auth.

Initial login:

```json
{
  "method": "account/login/start",
  "id": 7,
  "params": {
    "type": "chatgptAuthTokens",
    "idToken": "<jwt>",
    "accessToken": "<jwt>"
  }
}
```

If the server later needs fresh tokens, it sends a server request:

```json
{
  "method": "account/chatgptAuthTokens/refresh",
  "id": 8,
  "params": { "reason": "unauthorized", "previousAccountId": "org-123" }
}
```

The host must answer with fresh tokens:

```json
{
  "id": 8,
  "result": {
    "idToken": "<jwt>",
    "accessToken": "<jwt>"
  }
}
```

The server retries the original request after a successful refresh response.
Requests time out after about 10 seconds, so do not block the refresh path on slow UI.

This is usually the better default for browser-first web products that already have a server-side auth layer.

## Cancel Login

For managed ChatGPT login, cancel with:

```json
{
  "method": "account/login/cancel",
  "id": 4,
  "params": { "loginId": "<uuid>" }
}
```

## Logout

Send:

```json
{ "method": "account/logout", "id": 5 }
```

Then expect:

- empty success result
- `account/updated` with `authMode: null`

## Rate Limits

Use `account/rateLimits/read` to fetch the current view:

```json
{ "method": "account/rateLimits/read", "id": 6 }
```

Use `account/rateLimits/updated` to keep the UI current.

Useful fields:

- `limitId`
- `limitName`
- `primary.usedPercent`
- `primary.windowDurationMins`
- `primary.resetsAt`

If the host app promises that users can use their ChatGPT-backed access inside the app, rate-limit visibility should be part of the UX.

## UX Recommendations

- Always expose the current auth mode somewhere in debug or settings UI.
- Open managed ChatGPT login in the system browser, not an ad hoc embedded browser unless the product has a strong reason to own the full flow.
- Treat `account/login/completed` and `account/updated` as separate events. Both matter.
- Show a clear recovery path when external-token refresh fails.
- Do not imply that plan type or rate-limit state is a billing dashboard.
- For web apps, do not leak token refresh mechanics into browser code unless that is a deliberate and reviewed design choice.
