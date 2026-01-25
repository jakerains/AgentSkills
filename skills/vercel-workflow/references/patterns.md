# Workflow DevKit Patterns

## Table of Contents

1. [Chat Session Patterns](#chat-session-patterns)
2. [Parallel Processing](#parallel-processing)
3. [Saga Pattern](#saga-pattern)
4. [Circuit Breaker](#circuit-breaker)
5. [Scheduled/Recurring Workflows](#scheduledrecurring-workflows)
6. [Human-in-the-Loop](#human-in-the-loop)
7. [Polling with Backoff](#polling-with-backoff)
8. [Conditional Branching](#conditional-branching)
9. [Webhooks](#webhooks)
10. [Resumable AI Streams](#resumable-ai-streams)

---

## Chat Session Patterns

### Single-Turn (Stateless)

Each message triggers a new workflow. Client owns conversation history.

```typescript
// workflows/chat/single-turn.ts
export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";

  globalThis.fetch = fetch; // For AI SDK

  const agent = new DurableAgent({ /* config */ });
  const result = await agent.stream({
    messages,
    writable: getWritable()
  });

  return result.messages;
}

// API route - new workflow per request
export async function POST(request: Request) {
  const { messages } = await request.json();
  const run = await start(chatWorkflow, [messages]);
  return new Response(run.readable);
}
```

### Multi-Turn (Stateful)

Single workflow handles entire conversation. Workflow owns state.

```typescript
// workflows/chat/multi-turn.ts
import { defineHook, getWritable, fetch } from "workflow";
import { z } from "zod";

const messageHook = defineHook(z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string()
}));

export async function chatSessionWorkflow(sessionId: string) {
  "use workflow";

  globalThis.fetch = fetch;

  const messages: UIMessage[] = [];
  const writable = getWritable();

  // Wait for messages via hook
  for await (const newMessage of messageHook.create({
    token: `session:${sessionId}`
  })) {
    messages.push(newMessage);

    const agent = new DurableAgent({ /* config */ });
    const result = await agent.stream({ messages, writable });

    messages.push(...result.messages);
  }
}

// API routes:
// POST /api/chat - Start session
// POST /api/chat/[id] - Send message via hook
```

**When to use:**

| Pattern | Use When |
|---------|----------|
| Single-Turn | Adapting existing systems, simple Q&A |
| Multi-Turn | Production apps, full session observability, backend message injection |

---

## Parallel Processing (Fan-Out / Fan-In)

```typescript
export async function batchProcessWorkflow(items: string[]) {
  "use workflow";

  // Fan-out: Process items in parallel
  const results = await Promise.all(
    items.map(item => processItem(item))
  );

  // Fan-in: Aggregate results
  const summary = await aggregateResults(results);

  return summary;
}

async function processItem(item: string) {
  "use step";
  return { item, processed: true };
}

async function aggregateResults(results: ProcessResult[]) {
  "use step";
  return {
    total: results.length,
    successful: results.filter(r => r.processed).length
  };
}
```

---

## Saga Pattern (Compensating Transactions)

Handle failures with rollback logic:

```typescript
export async function orderSagaWorkflow(order: Order) {
  "use workflow";

  const reservationId = await reserveInventory(order);

  try {
    const paymentId = await processPayment(order);

    try {
      await shipOrder(order, reservationId);
      return { success: true, paymentId };
    } catch (e) {
      // Compensate: Refund payment
      await refundPayment(paymentId);
      throw e;
    }
  } catch (e) {
    // Compensate: Release inventory
    await releaseInventory(reservationId);
    throw e;
  }
}
```

---

## Circuit Breaker

Protect against cascading failures:

```typescript
interface CircuitState {
  failures: number;
  lastFailure: number;
  isOpen: boolean;
}

export async function resilientAPIWorkflow(endpoint: string) {
  "use workflow";

  const state = await getCircuitState(endpoint);

  if (state.isOpen) {
    const timeSinceFailure = Date.now() - state.lastFailure;
    if (timeSinceFailure < 60000) { // 1 minute cooldown
      throw new FatalError("Circuit breaker is open");
    }
  }

  try {
    const result = await callAPI(endpoint);
    await resetCircuit(endpoint);
    return result;
  } catch (error) {
    await recordFailure(endpoint);
    throw error;
  }
}
```

---

## Scheduled/Recurring Workflows

```typescript
export async function dailyReportWorkflow() {
  "use workflow";

  while (true) {
    const report = await generateDailyReport();
    await sendReport(report);

    // Sleep until next day at 9 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0);

    await sleep(tomorrow);
  }
}

// Start once, runs forever
const run = await start(dailyReportWorkflow);
```

---

## Human-in-the-Loop

```typescript
export async function contentModerationWorkflow(contentId: string) {
  "use workflow";

  const analysis = await analyzeContent(contentId);

  if (analysis.confidence < 0.9) {
    // Create approval hook
    const approvalHook = createHook<{
      approved: boolean;
      reason?: string;
    }>({
      token: `moderation:${contentId}`
    });

    // Notify moderator with hook token
    await notifyModerator(contentId, approvalHook.token, analysis);

    // Wait for human decision (can take days)
    const decision = await approvalHook;

    if (!decision.approved) {
      await rejectContent(contentId, decision.reason);
      return { status: "rejected" };
    }
  }

  await publishContent(contentId);
  return { status: "published" };
}

// API route for moderator to approve/reject
export async function POST(request: Request) {
  const { token, approved, reason } = await request.json();
  await resumeHook(token, { approved, reason });
  return Response.json({ success: true });
}
```

---

## Polling with Backoff

```typescript
import { sleep, FatalError } from "workflow";

export async function pollForResult(jobId: string) {
  "use workflow";

  let attempt = 0;
  const maxAttempts = 10;

  while (attempt < maxAttempts) {
    const result = await checkJobStatus(jobId);

    if (result.status === "complete") {
      return result.data;
    }

    if (result.status === "failed") {
      throw new FatalError(`Job failed: ${result.error}`);
    }

    attempt++;
    // Exponential backoff, max 1 minute
    await sleep(Math.min(1000 * 2 ** attempt, 60000));
  }

  throw new FatalError("Job did not complete in time");
}

async function checkJobStatus(jobId: string) {
  "use step";
  const res = await fetch(`https://api.example.com/jobs/${jobId}`);
  return res.json();
}
```

---

## Conditional Branching

```typescript
export async function orderWorkflow(order: Order) {
  "use workflow";

  const validation = await validateOrder(order);

  if (!validation.valid) {
    await notifyInvalidOrder(order.id);
    return { status: "rejected" };
  }

  // High-value orders need manager approval
  if (order.total > 1000) {
    const approvalHook = createHook<{ approved: boolean }>({
      token: `order-approval:${order.id}`
    });
    await requestManagerApproval(order.id, approvalHook.token);

    const approval = await approvalHook;
    if (!approval.approved) {
      return { status: "rejected" };
    }
  }

  await processOrder(order);
  return { status: "completed" };
}
```

---

## Webhooks

### Basic Webhook

```typescript
import { createWebhook } from "workflow";
import { resumeWebhook } from "workflow/api";

export async function githubWorkflow() {
  "use workflow";

  const webhook = createWebhook();

  // Register webhook URL with external service
  await registerGitHubWebhook(webhook.url);

  // Wait for webhook request
  const request = await webhook;

  await handleGitHubEvent(request);
}

async function handleGitHubEvent(request: RequestWithResponse) {
  "use step";

  const event = request.headers.get("X-GitHub-Event");
  const payload = await request.json();

  // Send response back to GitHub
  request.respondWith(
    Response.json({ received: true }, { status: 200 })
  );

  return { event, payload };
}

// API route to forward webhook
export async function POST(request: Request) {
  const token = new URL(request.url).searchParams.get("token");
  if (!token) {
    return Response.json({ error: "Missing token" }, { status: 400 });
  }
  return resumeWebhook(token, request);
}
```

### Webhook with Static Response

```typescript
const webhook = createWebhook({
  respondWith: Response.json({ success: true })
});
```

### Multiple Webhook Events

```typescript
export async function multiEventWorkflow() {
  "use workflow";

  const webhook = createWebhook();

  // Handle multiple webhook requests
  for await (const request of webhook) {
    const result = await processRequest(request);
    if (result.shouldStop) break;
  }
}
```

---

## Resumable AI Streams

Client-side reconnection for interrupted AI streams:

```typescript
// Client component
import { useChat } from "@ai-sdk/react";
import { WorkflowChatTransport } from "@workflow/ai";

function ChatComponent() {
  const [runId, setRunId] = useState<string | null>(null);

  const { messages, sendMessage, isLoading } = useChat({
    resume: !!runId, // Resume if we have a previous run ID

    transport: new WorkflowChatTransport({
      api: "/api/chat",
      maxConsecutiveErrors: 5,

      onChatSendMessage: (response, options) => {
        const workflowRunId = response.headers.get("x-workflow-run-id");
        if (workflowRunId) {
          setRunId(workflowRunId);
          localStorage.setItem("chat-run-id", workflowRunId);
        }
      },

      onChatEnd: ({ chatId, chunkIndex }) => {
        setRunId(null);
        localStorage.removeItem("chat-run-id");
      },

      // Add auth headers
      prepareSendMessagesRequest: async (config) => ({
        ...config,
        headers: {
          ...config.headers,
          "Authorization": `Bearer ${getToken()}`
        }
      })
    })
  });

  // Restore run ID on mount
  useEffect(() => {
    const savedRunId = localStorage.getItem("chat-run-id");
    if (savedRunId) setRunId(savedRunId);
  }, []);

  return (/* UI */);
}
```

**Server requirements:**
- Return `x-workflow-run-id` header from chat endpoint
- Default reconnect endpoint: `/api/chat/{runId}/stream`
