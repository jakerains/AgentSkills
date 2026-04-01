# Protocol and Events

Use this reference when implementing the JSON-RPC client, streaming UI, approvals, or event ordering.

## Wire Format

App Server uses JSON-RPC 2.0 semantics, but omits the `"jsonrpc": "2.0"` field on the wire.

### Request

```json
{ "method": "thread/start", "id": 10, "params": { "model": "gpt-5.4" } }
```

### Response

```json
{ "id": 10, "result": { "thread": { "id": "thr_123" } } }
```

### Error response

```json
{ "id": 10, "error": { "code": 123, "message": "Something went wrong" } }
```

### Notification

```json
{ "method": "turn/started", "params": { "turn": { "id": "turn_456" } } }
```

## Initialization

On each connection:

1. send `initialize`
2. wait for the result
3. send `initialized`

Important `initialize` fields:

- `clientInfo.name`
- `clientInfo.title`
- `clientInfo.version`
- optional `capabilities.experimentalApi`
- optional `capabilities.optOutNotificationMethods`

`clientInfo.name` is used for Compliance Logs identification in enterprise contexts.

## Thread Lifecycle

Primary methods:

- `thread/start`
- `thread/resume`
- `thread/fork`
- `thread/read`
- `thread/list`
- `thread/archive`
- `thread/unarchive`

Use `thread/start` for a new conversation.
Use `thread/resume` to continue an existing thread.
Use `thread/fork` when the product needs a branch of prior history.

## Turn Lifecycle

Primary methods:

- `turn/start`
- `turn/steer`
- `turn/interrupt`
- `review/start`

Recommended event loop:

1. call `turn/start`
2. keep reading notifications
3. update UI as `item/*` and `turn/*` notifications arrive
4. stop the busy state only when `turn/completed` arrives

## Items and Deltas

Common item types include:

- `userMessage`
- `agentMessage`
- `plan`
- `reasoning`
- `commandExecution`
- `fileChange`
- `mcpToolCall`
- `dynamicToolCall`
- `webSearch`
- `enteredReviewMode`
- `exitedReviewMode`

Treat `item/started` and `item/completed` as the authoritative lifecycle events.
Treat delta notifications as incremental patches to the current item.

Important delta notifications:

- `item/agentMessage/delta`
- `item/plan/delta`
- `item/reasoning/summaryTextDelta`
- `item/reasoning/textDelta`
- `item/commandExecution/outputDelta`

## Approvals

App Server can issue server requests to the client for approvals.

### Command approval order

1. `item/started` for a `commandExecution` item
2. `item/commandExecution/requestApproval`
3. client response with a decision
4. `serverRequest/resolved`
5. `item/completed`

### File change approval order

1. `item/started` for a `fileChange` item
2. `item/fileChange/requestApproval`
3. client response with a decision
4. `serverRequest/resolved`
5. `item/completed`

### Tool user input

Experimental `tool/requestUserInput` works the same way:

- App Server sends a server request
- the host answers
- App Server emits `serverRequest/resolved`

Design the host app to route these prompts by `threadId` and `turnId`.

## Backpressure and Retry

In WebSocket mode, request ingress is bounded. When the server is saturated it returns:

- error code `-32001`
- message `"Server overloaded; retry later."`

Treat this as retryable with exponential backoff and jitter.

## Experimental Features

The following patterns may require `experimentalApi` opt-in:

- some methods and fields
- dynamic tools
- `tool/requestUserInput`
- some collaboration and realtime surfaces

If the server rejects a request because the experimental capability is missing, update the handshake instead of working around the error at the request call site.
