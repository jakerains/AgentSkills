# Vercel Workflow DevKit - API Deep Dive

## Table of Contents

1. [workflow Package](#workflow-package)
2. [workflow/api Package](#workflowapi-package)
3. [workflow/next Package](#workflownext-package)
4. [@workflow/ai Package](#workflowai-package)

---

## workflow Package

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

// Date object - sleep until specific time
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

// Basic usage in workflow
const response = await fetch("https://api.example.com/data");
const data = await response.json();

// With options
const response = await fetch("https://api.example.com/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Alice" })
});

// CRITICAL: For AI SDK and other libraries that use fetch internally
export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";
  globalThis.fetch = fetch; // Enable fetch for libraries

  // Now AI SDK generateText, streamText, etc. will work
}
```

**Rules:**
- Use directly in workflows (it's a special step function)
- Automatically serializes response for replay
- For libraries that use fetch internally, assign to `globalThis.fetch`

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
import { RetryableError, getStepMetadata } from "workflow";

async function callExternalAPI() {
  "use step";

  const { attempt } = getStepMetadata();
  const response = await fetch("https://api.example.com/data");

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    throw new RetryableError("Rate limited", {
      retryAfter: retryAfter ? parseInt(retryAfter) * 1000 : "5m"
    });
  }

  if (response.status >= 500) {
    // Exponential backoff using attempt number
    throw new RetryableError("Server error", {
      retryAfter: (attempt ** 2) * 1000
    });
  }

  return response.json();
}
```

**retryAfter formats:**
- Duration string: `"5m"`, `"30s"`, `"1h"`
- Milliseconds: `5000`
- Date object: `new Date(Date.now() + 60000)`

---

### Step maxRetries Property

Customize retry count per step function:

```typescript
async function callApi(endpoint: string) {
  "use step";
  // ... step logic
}

callApi.maxRetries = 5; // Retry up to 5 times (6 total attempts)
// Default is 3 (4 total attempts)
// Set to 0 for no retries (1 attempt only)
```

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

  // Create typed hook with custom token for deterministic recovery
  const hook = createHook<ApprovalPayload>({
    token: `approval:${documentId}` // Optional: custom token
  });

  // Access the token to share with external system
  await notifyReviewer(documentId, hook.token);

  // Workflow suspends here until resumed
  const approval = await hook;

  if (approval.approved) {
    await publishDocument(documentId);
  }
}

// Multiple events with AsyncIterable
const hook = createHook<Message>();
for await (const message of hook) {
  if (message.type === "END") break;
  await processMessage(message);
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

Type-safe hook definition with runtime validation.

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

  const result = await hook; // Fully typed!

  if (result.status === "success") {
    await fulfillOrder(orderId, result.transactionId);
  }
}

// Resume from API route with validation
export async function POST(request: Request) {
  const { token, ...payload } = await request.json();
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

  // Register webhook URL with GitHub
  await registerGitHubWebhook(repoId, webhook.url);

  // Wait for webhook request
  const request = await webhook;

  // Process in step (must call respondWith!)
  await handlePREvent(request);
}

async function handlePREvent(request: RequestWithResponse) {
  "use step";

  const event = request.headers.get("X-GitHub-Event");
  const payload = await request.json();

  // REQUIRED: Send response
  request.respondWith(
    Response.json({ received: true }, { status: 200 })
  );

  return { event, payload };
}

// Static response option
const webhook = createWebhook({
  respondWith: Response.json({ success: true })
});

// Multiple webhook events
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

export async function progressWorkflow(items: string[]) {
  "use workflow";

  const writable = getWritable<{ progress: number; item: string }>();

  for (let i = 0; i < items.length; i++) {
    await processItem(items[i], writable, i, items.length);
  }

  await closeStream(writable);
}

// IMPORTANT: All stream operations must happen in steps
async function processItem(
  item: string,
  writable: WritableStream,
  index: number,
  total: number
) {
  "use step";

  const writer = writable.getWriter();

  try {
    await someAsyncOperation(item);
    await writer.write({
      progress: ((index + 1) / total) * 100,
      item
    });
  } finally {
    writer.releaseLock(); // Always release!
  }
}

async function closeStream(writable: WritableStream) {
  "use step";
  await writable.close();
}

// Namespaced streams for separate channels
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

  // Use for logging, external tracking, etc.
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

  const { stepId, attempt } = getStepMetadata();

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
  stepId: string;   // Unique, stable across retries
  attempt: number;  // Current attempt number (useful for backoff)
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

// With arguments (must be array)
const run = await start(myWorkflow, ["arg1", "arg2"]);

// With options
const run = await start(myWorkflow, ["arg1"], {
  deploymentId: "custom-deployment-id"
});

// Access run properties
console.log(run.id);           // Run ID
const status = await run.status; // Promise<RunStatus>
const result = await run.returnValue; // Blocks until completion
return new Response(run.readable); // Stream output
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

// Resume from specific point (for reconnection)
const resumed = run.getReadable({ startIndex: 50 });
```

---

### resumeHook(token, payload)

Resume a workflow by sending payload to a hook.

```typescript
import { resumeHook } from "workflow/api";

// Basic
const result = await resumeHook(token, { approved: true });

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

  // Returns the Response from the workflow's respondWith()
  return resumeWebhook(token, request);
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
  reactStrictMode: true,
};

export default withWorkflow(nextConfig);
```

This configures webpack/turbopack to transform `"use workflow"` and `"use step"` directives.

---

## @workflow/ai Package

### DurableAgent

Build resilient AI agents with persistent state.

```typescript
import { DurableAgent } from "@workflow/ai/agent";
import { getWritable, fetch } from "workflow";
import { z } from "zod";
import type { UIMessageChunk } from "ai";

export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";

  // CRITICAL: Enable fetch for AI SDK
  globalThis.fetch = fetch;

  const agent = new DurableAgent({
    model: "anthropic/claude-haiku-4.5", // Vercel AI Gateway format
    system: "You are a helpful assistant.",
    temperature: 0.7,
    maxOutputTokens: 1000,

    tools: {
      searchWeb: {
        description: "Search the web",
        inputSchema: z.object({ query: z.string() }),
        execute: async ({ query }) => {
          "use step"; // Auto-retry on failure
          return await searchAPI(query);
        }
      }
    },

    toolChoice: "auto" // or "required", "none", { type: "tool", toolName: "..." }
  });

  const writable = getWritable<UIMessageChunk>();

  const result = await agent.stream({
    messages,
    writable,
    maxSteps: 10, // IMPORTANT: Default is unlimited!

    // Optional callbacks
    onStepFinish: async (step) => {
      console.log(`Step finished: ${step.finishReason}`);
    },
    onFinish: async ({ steps, messages }) => {
      console.log(`Completed with ${steps.length} steps`);
    },
    onError: async ({ error }) => {
      console.error("Stream error:", error);
    }
  });

  return result.messages;
}
```

**Key DurableAgent Options:**

| Option | Type | Description |
|--------|------|-------------|
| `model` | `string \| (() => Promise<LanguageModel>)` | Model provider (Vercel Gateway format or custom) |
| `system` | `string` | System prompt |
| `tools` | `ToolSet` | Available tools |
| `toolChoice` | `"auto" \| "required" \| "none" \| {type, toolName}` | Tool choice strategy |
| `temperature` | `number` | Sampling temperature |
| `maxOutputTokens` | `number` | Max tokens to generate |
| `topP` | `number` | Nucleus sampling |
| `stopSequences` | `string[]` | Stop generation triggers |

**Key Stream Options:**

| Option | Type | Description |
|--------|------|-------------|
| `messages` | `UIMessage[]` | Conversation messages |
| `writable` | `WritableStream` | Output stream |
| `maxSteps` | `number` | Max LLM calls (default: unlimited!) |
| `activeTools` | `string[]` | Limit available tools |
| `prepareStep` | `(info) => PrepareStepResult` | Modify settings per step |
| `collectUIMessages` | `boolean` | Accumulate UIMessage[] for persistence |
| `experimental_output` | `OutputSpecification` | Structured output parsing |

---

### prepareStep Callback

Modify settings dynamically before each LLM call:

```typescript
await agent.stream({
  messages,
  writable: getWritable<UIMessageChunk>(),
  prepareStep: async ({ stepNumber, messages, steps }) => {
    // Switch to stronger model for complex reasoning
    if (stepNumber > 2 && messages.length > 10) {
      return { model: "anthropic/claude-sonnet-4.5" };
    }

    // Trim context if too large
    if (messages.length > 20) {
      return {
        messages: [
          messages[0], // Keep system message
          ...messages.slice(-10) // Keep last 10
        ]
      };
    }

    return {}; // No changes
  }
});
```

---

### Structured Output

Parse structured data from LLM responses:

```typescript
import { DurableAgent, Output } from "@workflow/ai/agent";

const result = await agent.stream({
  messages: [{ role: "user", content: "Analyze sentiment: 'I love this!'" }],
  writable: getWritable<UIMessageChunk>(),
  experimental_output: Output.object({
    schema: z.object({
      sentiment: z.enum(["positive", "negative", "neutral"]),
      confidence: z.number().min(0).max(1),
      reasoning: z.string()
    })
  })
});

// Access parsed output
console.log(result.experimental_output);
// { sentiment: "positive", confidence: 0.95, reasoning: "..." }
```

---

### Collecting UI Messages

Persist conversations without re-reading the stream:

```typescript
const result = await agent.stream({
  messages,
  writable: getWritable<UIMessageChunk>(),
  collectUIMessages: true // Enable accumulation
});

// Access accumulated messages
const uiMessages: UIMessage[] = result.uiMessages ?? [];
await saveConversation(uiMessages);
```

---

### Step-Level vs Workflow-Level Tools

| Capability | Step-Level (`"use step"`) | Workflow-Level (no directive) |
|------------|---------------------------|-------------------------------|
| `getWritable()` | ✅ | ❌ |
| Automatic retries | ✅ | ❌ |
| Side-effects (API calls) | ✅ | ❌ |
| `sleep()` | ❌ | ✅ |
| `createWebhook()` | ❌ | ✅ |
| `createHook()` | ❌ | ✅ |

**Combine both levels:**

```typescript
tools: {
  scheduleTask: {
    description: "Schedule a task with delay",
    inputSchema: z.object({ delaySeconds: z.number() }),
    execute: async ({ delaySeconds }) => {
      // NO "use step" - runs at workflow level
      await sleep(`${delaySeconds}s`);
      return `Slept for ${delaySeconds} seconds`;
    }
  },
  fetchData: {
    description: "Fetch data from API",
    inputSchema: z.object({ url: z.string() }),
    execute: async ({ url }) => {
      "use step"; // Runs at step level with retries
      const res = await fetch(url);
      return res.json();
    }
  }
}
```

---

### WorkflowChatTransport

Reliable chat transport with automatic reconnection:

```typescript
import { useChat } from "@ai-sdk/react";
import { WorkflowChatTransport } from "@workflow/ai";

function ChatComponent() {
  const [runId, setRunId] = useState<string | null>(null);

  const { messages, sendMessage, isLoading } = useChat({
    resume: !!runId,

    transport: new WorkflowChatTransport({
      api: "/api/chat",
      maxConsecutiveErrors: 5,

      onChatSendMessage: (response) => {
        const workflowRunId = response.headers.get("x-workflow-run-id");
        if (workflowRunId) {
          setRunId(workflowRunId);
          localStorage.setItem("chat-run-id", workflowRunId);
        }
      },

      onChatEnd: () => {
        setRunId(null);
        localStorage.removeItem("chat-run-id");
      },

      prepareSendMessagesRequest: async (config) => ({
        ...config,
        headers: {
          ...config.headers,
          "Authorization": `Bearer ${getToken()}`
        }
      })
    })
  });

  return (/* UI */);
}
```

**Requirements:**
- Chat endpoint must return `x-workflow-run-id` header
- Default reconnect endpoint: `/api/chat/{runId}/stream`
