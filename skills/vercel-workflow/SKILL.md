---
name: vercel-workflow
description: Build durable workflows with Vercel Workflow DevKit using "use workflow" and "use step" directives. Use for long-running tasks, background jobs, AI agents, webhooks, scheduled tasks, retries, and workflow orchestration in Next.js apps.
---

# Vercel Workflow DevKit

Build durable, resumable workflows that survive restarts, deployments, and infrastructure failures using simple TypeScript directives.

## Quick Start (Next.js)

### 1. Install

```bash
npm i workflow
```

### 2. Configure next.config.ts

```typescript
import { withWorkflow } from "workflow/next";

const nextConfig = {};

export default withWorkflow(nextConfig);
```

### 3. Create Your First Workflow

```typescript
// workflows/user-signup.ts
import { sleep, FatalError } from "workflow";

export async function userSignupWorkflow(email: string) {
  "use workflow";

  const user = await createUser(email);
  await sendWelcomeEmail(user.id, email);

  // Sleep without consuming resources (can be seconds to months)
  await sleep("3d");

  await sendFollowUpEmail(user.id, email);
  return { success: true, oderId: user.id };
}

async function createUser(email: string) {
  "use step";
  // Business logic - automatically retried on failure
  return { id: crypto.randomUUID(), email };
}

async function sendWelcomeEmail(userId: string, email: string) {
  "use step";
  const res = await fetch("https://api.email.com/send", {
    method: "POST",
    body: JSON.stringify({ to: email, template: "welcome" })
  });
  if (!res.ok) throw new Error("Email failed"); // Auto-retried
}

async function sendFollowUpEmail(userId: string, email: string) {
  "use step";
  // Intentional failures should throw FatalError (no retry)
  if (!email.includes("@")) {
    throw new FatalError("Invalid email format");
  }
  // ... send email
}
```

### 4. Create API Route Handler

```typescript
// app/api/signup/route.ts
import { start } from "workflow/api";
import { userSignupWorkflow } from "@/workflows/user-signup";

export async function POST(request: Request) {
  const { email } = await request.json();
  const run = await start(userSignupWorkflow, [email]);
  return Response.json({ runId: run.id });
}
```

### 5. Run and Observe

```bash
npm run dev
curl -X POST --json '{"email":"user@example.com"}' http://localhost:3000/api/signup

# Observe workflows
npx workflow web          # Web UI
npx workflow inspect runs # CLI
```

## Core Concepts

### Directives

| Directive | Purpose | Execution |
|-----------|---------|-----------|
| `"use workflow"` | Orchestrates steps, can sleep/suspend | Deterministic, replay-safe |
| `"use step"` | Contains business logic, side effects | Runs on separate request, auto-retried |

### Key Rules

1. **Workflows are orchestrators** - They coordinate steps but don't perform side effects
2. **Steps contain business logic** - All external calls, I/O, and side effects go in steps
3. **Steps auto-retry** - Unhandled errors trigger automatic retries
4. **Workflows are deterministic** - Must produce same step sequence on replay

## API Reference

### workflow package

```typescript
import {
  sleep,              // Suspend workflow for duration/until date
  fetch,              // HTTP requests with auto-retry (use in workflows)
  FatalError,         // Non-retryable error
  RetryableError,     // Explicit retry with delay
  createHook,         // Receive payloads from external systems
  createWebhook,      // Receive HTTP requests
  defineHook,         // Type-safe hook helper
  getWritable,        // Access workflow's output stream
  getWorkflowMetadata,// Get workflow run context
  getStepMetadata     // Get step execution context
} from "workflow";
```

### workflow/api package

```typescript
import {
  start,          // Start a new workflow run
  getRun,         // Get workflow run status
  resumeHook,     // Resume workflow via hook
  resumeWebhook,  // Resume workflow via webhook
  getHookByToken, // Get hook details
  getWorld        // Access storage/queuing backends
} from "workflow/api";
```

## Sleep & Scheduling

```typescript
// Duration strings
await sleep("10s");   // 10 seconds
await sleep("5m");    // 5 minutes
await sleep("2h");    // 2 hours
await sleep("1d");    // 1 day
await sleep("30d");   // 30 days

// Milliseconds
await sleep(5000);    // 5 seconds

// Until specific date
await sleep(new Date("2024-12-25"));
```

## Error Handling

```typescript
import { FatalError, RetryableError } from "workflow";

async function processPayment(amount: number) {
  "use step";

  try {
    const result = await paymentAPI.charge(amount);
    return result;
  } catch (error) {
    // Don't retry invalid requests
    if (error.code === "INVALID_CARD") {
      throw new FatalError("Invalid card number");
    }

    // Explicit retry with delay
    if (error.code === "RATE_LIMITED") {
      throw new RetryableError("Rate limited", {
        retryAfter: "5m"  // or milliseconds or Date
      });
    }

    // Other errors auto-retry with default backoff
    throw error;
  }
}
```

### Custom Fetch Wrapper for APIs

```typescript
async function apiFetch(url: string, options?: RequestInit) {
  "use step";

  const response = await fetch(url, options);

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    throw new RetryableError("Rate limited", {
      retryAfter: retryAfter ? parseInt(retryAfter) * 1000 : "1m"
    });
  }

  if (response.status >= 400 && response.status < 500) {
    throw new FatalError(`Client error: ${response.status}`);
  }

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  return response.json();
}
```

## Hooks & Webhooks

### Hooks (Arbitrary Payloads)

```typescript
import { createHook } from "workflow";
import { resumeHook } from "workflow/api";

// In workflow
export async function approvalWorkflow(orderId: string) {
  "use workflow";

  const hook = createHook<{ approved: boolean; comment: string }>();
  console.log("Approval token:", hook.token);

  // Workflow suspends here until hook is resumed
  const result = await hook;

  if (result.approved) {
    await processOrder(orderId);
  }
}

// In API route to resume
export async function POST(request: Request) {
  const { token, approved, comment } = await request.json();
  await resumeHook(token, { approved, comment });
  return Response.json({ success: true });
}
```

### Type-Safe Hooks with defineHook

```typescript
import { defineHook } from "workflow";
import { z } from "zod";

// Define once, use everywhere
export const approvalHook = defineHook(
  z.object({
    approved: z.boolean(),
    comment: z.string().min(1).max(500)
  })
);

// In workflow
const hook = approvalHook.create();
const result = await hook;

// In API route
await approvalHook.resume(token, { approved: true, comment: "LGTM" });
```

### Webhooks (HTTP Requests)

```typescript
import { createWebhook } from "workflow";
import { resumeWebhook } from "workflow/api";

export async function githubWorkflow() {
  "use workflow";

  const webhook = createWebhook();
  console.log("Webhook URL token:", webhook.token);

  // Wait for HTTP request
  const request = await webhook;

  await handleRequest(request);
}

async function handleRequest(request: RequestWithResponse) {
  "use step";

  const body = await request.json();
  // Process webhook payload

  // Send response
  request.respondWith(Response.json({ received: true }));
}

// In API route
export async function POST(request: Request) {
  const token = new URL(request.url).searchParams.get("token");
  return resumeWebhook(token!, request);
}
```

## Streaming

```typescript
import { getWritable } from "workflow";

export async function streamingWorkflow() {
  "use workflow";

  const writable = getWritable();
  await streamProgress(writable);
  await closeStream(writable);
}

async function streamProgress(writable: WritableStream) {
  "use step";

  const writer = writable.getWriter();

  for (let i = 0; i <= 100; i += 10) {
    await writer.write({ progress: i });
    await new Promise(r => setTimeout(r, 500));
  }

  writer.releaseLock();
}

async function closeStream(writable: WritableStream) {
  "use step";
  await writable.close();
}

// Consume in API route
export async function GET() {
  const run = await start(streamingWorkflow);
  return new Response(run.readable);
}
```

### Namespaced Streams

```typescript
const dataStream = getWritable({ namespace: "data" });
const logsStream = getWritable({ namespace: "logs" });

// Consume specific namespace
const readable = run.getReadable({ namespace: "logs" });
```

## Idempotency

Use `stepId` for idempotency keys to prevent duplicate operations:

```typescript
import { getStepMetadata } from "workflow";

async function chargeCustomer(customerId: string, amount: number) {
  "use step";

  const { stepId } = getStepMetadata();

  // stepId is stable across retries, unique per step
  return stripe.charges.create({
    customer: customerId,
    amount,
    idempotency_key: `charge:${stepId}`
  });
}
```

## Serialization Rules

All workflow/step arguments and return values must be serializable:

**Supported types:**
- JSON types (string, number, boolean, null, arrays, objects)
- undefined, bigint, Date, RegExp, URL
- Map, Set, typed arrays, ArrayBuffer
- Headers, Request, Response
- ReadableStream, WritableStream

**Important:** Data is passed by value. Mutations in steps don't affect workflow variables:

```typescript
// WRONG - changes lost
async function workflow() {
  "use workflow";
  const user = { name: "Alice" };
  await updateUser(user);
  console.log(user.name); // Still "Alice"
}

// CORRECT - return modified data
async function workflow() {
  "use workflow";
  let user = { name: "Alice" };
  user = await updateUser(user);
  console.log(user.name); // "Bob"
}

async function updateUser(user: User) {
  "use step";
  user.name = "Bob";
  return user; // Must return
}
```

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

No additional configuration needed. Vercel World automatically provides:
- Scalable storage
- Distributed queuing
- Multi-environment support (production, preview, development)

### Inspect Production Workflows

```bash
npx workflow inspect runs --backend vercel --env production
```

### Other Environments

Set `WORKFLOW_TARGET_WORLD` environment variable:
- `@workflow/world-local` - Local filesystem (default for dev)
- `@workflow-worlds/postgres` - PostgreSQL
- `@workflow-worlds/turso` - Turso/SQLite
- `@workflow-worlds/mongodb` - MongoDB
- `@workflow-worlds/redis` - Redis

## AI Agents with @workflow/ai

### DurableAgent

```typescript
import { DurableAgent } from "@workflow/ai";
import { getWritable } from "workflow";

export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";

  const writable = getWritable<UIMessageChunk>();

  const agent = new DurableAgent({
    model: "anthropic/claude-haiku-4.5",
    system: "You are a helpful assistant.",
    tools: {
      searchWeb: {
        description: "Search the web",
        parameters: z.object({ query: z.string() }),
        execute: async ({ query }) => {
          "use step";
          return await searchAPI(query);
        }
      }
    }
  });

  const result = await agent.stream({
    messages,
    writable,
    maxSteps: 10
  });

  return result.messages;
}
```

### WorkflowChatTransport

Automatic reconnection for interrupted AI streams:

```typescript
import { useChat } from "@ai-sdk/react";
import { WorkflowChatTransport } from "@workflow/ai";

export default function Chat() {
  const { messages, sendMessage } = useChat({
    transport: new WorkflowChatTransport({
      maxConsecutiveErrors: 5,
      onChatSendMessage: (response, options) => {
        const runId = response.headers.get("x-workflow-run-id");
        localStorage.setItem("workflow-run-id", runId!);
      }
    })
  });

  // ...
}
```

## Common Patterns

### Parallel Steps

```typescript
export async function parallelWorkflow() {
  "use workflow";

  // Steps run in parallel
  const [users, products, orders] = await Promise.all([
    fetchUsers(),
    fetchProducts(),
    fetchOrders()
  ]);

  return { users, products, orders };
}
```

### Conditional Branching

```typescript
export async function orderWorkflow(order: Order) {
  "use workflow";

  const validation = await validateOrder(order);

  if (!validation.valid) {
    await notifyInvalidOrder(order.id);
    return { status: "rejected" };
  }

  if (order.total > 1000) {
    await requestManagerApproval(order.id);
  }

  await processOrder(order);
  return { status: "completed" };
}
```

### Polling with Backoff

```typescript
export async function pollForResult(jobId: string) {
  "use workflow";

  let attempt = 0;
  const maxAttempts = 10;

  while (attempt < maxAttempts) {
    const result = await checkJobStatus(jobId);

    if (result.status === "complete") {
      return result.data;
    }

    attempt++;
    // Exponential backoff, max 1 minute
    await sleep(Math.min(1000 * 2 ** attempt, 60000));
  }

  throw new FatalError("Job did not complete in time");
}
```

## Troubleshooting

### Next.js 16.1+ Compatibility

```
Error: Cannot find module 'next/dist/lib/server-external-packages.json'
```

**Fix:** Upgrade workflow package:
```bash
npm install workflow@latest
```

### Node.js Module in Workflow Error

```
Cannot use Node.js module "fs" in workflow functions
```

**Fix:** Move Node.js operations to step functions:

```typescript
// WRONG
export async function workflow() {
  "use workflow";
  fs.readFileSync("file.txt"); // Error!
}

// CORRECT
export async function workflow() {
  "use workflow";
  const content = await readFile("file.txt");
}

async function readFile(path: string) {
  "use step";
  return fs.readFileSync(path, "utf-8");
}
```

### Middleware Configuration

If using a proxy handler, exclude workflow paths:

```typescript
// middleware.ts
export const config = {
  matcher: ['/((?!.well-known/workflow).*)']
};
```

## TypeScript Setup (Optional)

Add to `tsconfig.json` for IntelliSense:

```json
{
  "compilerOptions": {
    "plugins": [{ "name": "workflow/ts-plugin" }]
  }
}
```

## References

- [Official Docs](https://useworkflow.dev/docs)
- [API Reference](https://useworkflow.dev/docs/api-reference)
- [GitHub Examples](https://github.com/vercel/workflow-examples)
- [Vercel Workflow Docs](https://vercel.com/docs/workflow)
