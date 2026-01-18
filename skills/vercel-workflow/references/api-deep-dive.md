# Vercel Workflow DevKit - API Deep Dive

## workflow Package Complete Reference

### sleep(duration)

Suspends workflow execution without consuming resources.

```typescript
import { sleep } from "workflow";

// String durations
await sleep("100ms");  // milliseconds
await sleep("30s");    // seconds
await sleep("5m");     // minutes
await sleep("2h");     // hours
await sleep("1d");     // days
await sleep("2w");     // weeks (14 days)

// Numeric (milliseconds)
await sleep(5000);

// Date object
await sleep(new Date("2025-01-01T00:00:00Z"));
await sleep(new Date(Date.now() + 60_000)); // 1 minute from now
```

**Rules:**
- Must be called directly inside workflow functions
- Cannot be called inside step functions
- Deterministic and replay-safe

---

### fetch(url, options)

HTTP requests with automatic serialization and retry semantics.

```typescript
import { fetch } from "workflow";

// Basic usage
const response = await fetch("https://api.example.com/data");
const data = await response.json();

// With options
const response = await fetch("https://api.example.com/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Alice" })
});
```

**Rules:**
- Special step function - call directly in workflows
- Returns standard Response object
- Automatically serializes response for replay

---

### FatalError

Marks a step as permanently failed (no retry).

```typescript
import { FatalError } from "workflow";

async function validateInput(data: unknown) {
  "use step";

  if (!data || typeof data !== "object") {
    throw new FatalError("Invalid input: must be an object");
  }

  if (!("email" in data)) {
    throw new FatalError("Missing required field: email");
  }

  return data;
}
```

**Constructor:**
```typescript
new FatalError(message: string)
```

**Use when:**
- Input validation fails
- Resource doesn't exist (404)
- Authentication fails (401, 403)
- Business rule violation
- Any error where retrying won't help

---

### RetryableError

Marks a step for explicit retry with configurable delay.

```typescript
import { RetryableError } from "workflow";

async function callExternalAPI() {
  "use step";

  const response = await fetch("https://api.example.com/data");

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    throw new RetryableError("Rate limited", {
      retryAfter: retryAfter ? parseInt(retryAfter) * 1000 : "5m"
    });
  }

  if (response.status === 503) {
    throw new RetryableError("Service unavailable", {
      retryAfter: "30s"
    });
  }

  return response.json();
}
```

**Constructor:**
```typescript
new RetryableError(message: string, options?: {
  retryAfter?: string | number | Date
})
```

**retryAfter formats:**
- Duration string: `"5m"`, `"30s"`, `"1h"`
- Milliseconds: `5000`
- Date object: `new Date(Date.now() + 60000)`

---

### createHook<T>()

Creates a hook to receive arbitrary payloads from external systems.

```typescript
import { createHook } from "workflow";

interface ApprovalPayload {
  approved: boolean;
  reviewerId: string;
  comment?: string;
}

export async function approvalWorkflow(documentId: string) {
  "use workflow";

  // Create typed hook
  const hook = createHook<ApprovalPayload>();

  // Access the token to share with external system
  await notifyReviewer(documentId, hook.token);

  // Workflow suspends here until resumed
  const approval = await hook;

  if (approval.approved) {
    await publishDocument(documentId);
  } else {
    await rejectDocument(documentId, approval.comment);
  }
}

// Custom token for deterministic identification
const hook = createHook<PaymentResult>({
  token: `payment:${orderId}:${customerId}`
});

// Waiting for multiple payloads
const hook = createHook<Message>();
const messages: Message[] = [];

for await (const message of hook) {
  messages.push(message);
  if (message.type === "END") break;
}
```

**Options:**
```typescript
interface HookOptions {
  token?: string;      // Custom token (default: auto-generated)
  metadata?: unknown;  // User-defined metadata
}
```

---

### defineHook(schema)

Type-safe hook definition with optional runtime validation.

```typescript
import { defineHook } from "workflow";
import { z } from "zod";

// Define hook schema once
export const paymentHook = defineHook(
  z.object({
    transactionId: z.string().uuid(),
    status: z.enum(["success", "failed", "pending"]),
    amount: z.number().positive(),
    currency: z.string().length(3)
  })
);

// Use in workflow
export async function paymentWorkflow(orderId: string) {
  "use workflow";

  const hook = paymentHook.create({
    token: `payment:${orderId}`
  });

  const result = await hook;
  // result is fully typed!

  if (result.status === "success") {
    await fulfillOrder(orderId, result.transactionId);
  }
}

// Resume from API route with validation
export async function POST(request: Request) {
  const { token, ...payload } = await request.json();

  // Validates payload against schema before resuming
  const result = await paymentHook.resume(token, payload);

  return Response.json({ runId: result.runId });
}
```

---

### createWebhook()

Creates an HTTP webhook endpoint that suspends the workflow.

```typescript
import { createWebhook } from "workflow";

export async function githubPRWorkflow(repoId: string) {
  "use workflow";

  const webhook = createWebhook();

  // Register webhook with GitHub
  await registerGitHubWebhook(repoId, webhook.token);

  // Wait for webhook request
  const request = await webhook;

  // Process in step
  await handlePREvent(request);
}

async function handlePREvent(request: RequestWithResponse) {
  "use step";

  const event = request.headers.get("X-GitHub-Event");
  const payload = await request.json();

  // Send response back to GitHub
  request.respondWith(
    Response.json({ received: true }, { status: 200 })
  );

  return { event, payload };
}

// Handle multiple webhook requests
for await (const request of webhook) {
  const result = await processRequest(request);
  if (result.shouldStop) break;
}
```

---

### getWritable<T>()

Access the workflow's output stream for real-time data delivery.

```typescript
import { getWritable } from "workflow";

// Basic usage
export async function progressWorkflow(items: string[]) {
  "use workflow";

  const writable = getWritable<{ progress: number; item: string }>();

  for (let i = 0; i < items.length; i++) {
    await processItem(items[i], writable, i, items.length);
  }

  await closeStream(writable);
}

async function processItem(
  item: string,
  writable: WritableStream,
  index: number,
  total: number
) {
  "use step";

  const writer = writable.getWriter();

  // Do work...
  await someAsyncOperation(item);

  // Write progress
  await writer.write({
    progress: ((index + 1) / total) * 100,
    item
  });

  writer.releaseLock(); // Always release!
}

async function closeStream(writable: WritableStream) {
  "use step";
  await writable.close();
}

// Namespaced streams
const dataStream = getWritable({ namespace: "data" });
const logsStream = getWritable({ namespace: "logs" });
```

**Important:**
- Workflows can get the stream but NOT interact with it directly
- All read/write operations must happen in steps
- Always release writer locks after writing

---

### getWorkflowMetadata()

Access workflow execution context.

```typescript
import { getWorkflowMetadata } from "workflow";

export async function trackedWorkflow(input: string) {
  "use workflow";

  const metadata = getWorkflowMetadata();

  console.log("Run ID:", metadata.workflowRunId);
  console.log("Started at:", metadata.workflowStartedAt);
  console.log("URL:", metadata.url);

  await logToExternalService({
    runId: metadata.workflowRunId,
    input
  });

  return processInput(input);
}
```

**Returns:**
```typescript
interface WorkflowMetadata {
  workflowRunId: string;      // Unique run identifier
  workflowStartedAt: Date;    // When run started
  url: string;                // Workflow trigger URL
}
```

---

### getStepMetadata()

Access step execution context (only in steps).

```typescript
import { getStepMetadata } from "workflow";

async function idempotentPayment(customerId: string, amount: number) {
  "use step";

  const { stepId } = getStepMetadata();

  // stepId is stable across retries, unique per step invocation
  return stripe.charges.create({
    customer: customerId,
    amount,
    currency: "usd",
    idempotency_key: `charge:${stepId}`
  });
}
```

**Returns:**
```typescript
interface StepMetadata {
  stepId: string;  // Unique, stable across retries
}
```

---

## workflow/api Package

### start(workflow, args?, options?)

Start a new workflow run.

```typescript
import { start } from "workflow/api";
import { myWorkflow } from "@/workflows/my-workflow";

// Basic
const run = await start(myWorkflow);

// With arguments
const run = await start(myWorkflow, ["arg1", "arg2"]);

// With options
const run = await start(myWorkflow, ["arg1"], {
  deploymentId: "custom-deployment-id"
});

// Access run properties
console.log(run.id);          // Run ID
console.log(run.status);      // Promise<RunStatus>
console.log(run.readable);    // ReadableStream for output
```

**Important:** Returns immediately after enqueueing - doesn't wait for completion.

---

### getRun(runId)

Get workflow run status without waiting.

```typescript
import { getRun } from "workflow/api";

const run = getRun(runId);

// Get status (async)
const status = await run.status;

// Get output stream
const readable = run.readable;

// Get namespaced stream
const logs = run.getReadable({ namespace: "logs" });

// Resume from specific point
const resumed = run.getReadable({ startIndex: 50 });
```

---

### resumeHook(token, payload)

Resume a workflow by sending payload to a hook.

```typescript
import { resumeHook } from "workflow/api";

// Basic
const result = await resumeHook(token, { approved: true });

// Typed
const result = await resumeHook<ApprovalPayload>(token, {
  approved: true,
  comment: "Looks good!"
});

// Returns
console.log(result.runId);  // ID of resumed workflow run
```

**Must be called outside workflow functions** (e.g., in API routes).

---

### resumeWebhook(token, request)

Resume a workflow by forwarding an HTTP request.

```typescript
import { resumeWebhook } from "workflow/api";

export async function POST(request: Request) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");

  if (!token) {
    return Response.json({ error: "Missing token" }, { status: 400 });
  }

  try {
    // Returns the Response from the workflow's respondWith()
    return resumeWebhook(token, request);
  } catch (error) {
    return Response.json({ error: "Webhook not found" }, { status: 404 });
  }
}
```

---

### getHookByToken(token)

Get hook details before resuming.

```typescript
import { getHookByToken } from "workflow/api";

const hook = await getHookByToken(token);

if (!hook) {
  return Response.json({ error: "Invalid token" }, { status: 404 });
}

console.log(hook.runId);     // Associated workflow run
console.log(hook.metadata);  // User-defined metadata
```

---

## workflow/next Package

### withWorkflow(config)

Wrap Next.js config to enable workflow directives.

```typescript
// next.config.ts
import { withWorkflow } from "workflow/next";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Your existing config
  reactStrictMode: true,
  experimental: {
    // ...
  }
};

export default withWorkflow(nextConfig);
```

This configures webpack/turbopack to transform `"use workflow"` and `"use step"` directives.

---

## @workflow/ai Package

### DurableAgent

Build resilient AI agents with persistent state.

```typescript
import { DurableAgent } from "@workflow/ai";
import { z } from "zod";

const agent = new DurableAgent({
  model: "anthropic/claude-haiku-4.5",
  system: "You are a helpful flight booking assistant.",
  temperature: 0.7,
  maxOutputTokens: 1000,

  tools: {
    searchFlights: {
      description: "Search for available flights",
      parameters: z.object({
        origin: z.string().length(3),
        destination: z.string().length(3),
        date: z.string()
      }),
      execute: async ({ origin, destination, date }) => {
        "use step";  // Auto-retry on failure
        return await flightAPI.search(origin, destination, date);
      }
    },

    bookFlight: {
      description: "Book a flight",
      parameters: z.object({
        flightId: z.string(),
        passengers: z.number()
      }),
      execute: async ({ flightId, passengers }) => {
        "use step";
        return await flightAPI.book(flightId, passengers);
      }
    }
  },

  toolChoice: "auto"  // or "required", "none", { type: "tool", toolName: "..." }
});

// Stream response
const result = await agent.stream({
  messages: conversationHistory,
  writable: getWritable(),
  maxSteps: 10,

  prepareStep: async (step) => {
    // Modify settings before each LLM call
    return {
      ...step,
      temperature: step.stepIndex > 0 ? 0.5 : 0.7
    };
  },

  onFinish: (result) => {
    console.log("Agent finished:", result.finishReason);
  },

  onError: (error) => {
    console.error("Agent error:", error);
  }
});

// Access results
console.log(result.messages);  // Full conversation
console.log(result.steps);     // Individual LLM calls
```

---

### WorkflowChatTransport

Reliable chat transport with automatic reconnection.

```typescript
import { useChat } from "@ai-sdk/react";
import { WorkflowChatTransport } from "@workflow/ai";

function ChatComponent() {
  const [runId, setRunId] = useState<string | null>(null);

  const { messages, sendMessage, isLoading } = useChat({
    // Resume if we have a previous run ID
    resume: !!runId,

    transport: new WorkflowChatTransport({
      api: "/api/chat",  // Default endpoint

      maxConsecutiveErrors: 5,  // Retry attempts

      onChatSendMessage: (response, options) => {
        // Extract and store run ID for resumption
        const workflowRunId = response.headers.get("x-workflow-run-id");
        if (workflowRunId) {
          setRunId(workflowRunId);
          localStorage.setItem("chat-run-id", workflowRunId);
        }
      },

      onChatEnd: ({ chatId, chunkIndex }) => {
        console.log(`Chat ${chatId} finished with ${chunkIndex} chunks`);
        setRunId(null);
        localStorage.removeItem("chat-run-id");
      },

      prepareSendMessagesRequest: async (config) => ({
        ...config,
        headers: {
          ...config.headers,
          "Authorization": `Bearer ${getToken()}`
        }
      }),

      prepareReconnectToStreamRequest: async (config) => ({
        ...config,
        headers: {
          ...config.headers,
          "Authorization": `Bearer ${getToken()}`
        }
      })
    })
  });

  // ...
}
```

**Requirements:**
- Chat endpoint must return `x-workflow-run-id` header
- Default reconnect endpoint: `/api/chat/{runId}/stream`
