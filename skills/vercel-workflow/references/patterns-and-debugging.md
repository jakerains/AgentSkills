# Workflow DevKit Patterns & Debugging Guide

## Architecture Patterns

### Single-Turn vs Multi-Turn Chat Sessions

**Single-Turn:** Each message triggers a new workflow run. Client owns conversation history.

```typescript
// workflows/chat/single-turn.ts
export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";

  const agent = new DurableAgent({ /* config */ });
  const result = await agent.stream({ messages, writable: getWritable() });

  return result.messages;
}

// API route starts new workflow per message
export async function POST(request: Request) {
  const { messages } = await request.json();
  const run = await start(chatWorkflow, [messages]);
  return new Response(run.readable);
}
```

**Multi-Turn:** Single workflow handles entire conversation. Workflow owns state.

```typescript
// workflows/chat/multi-turn.ts
import { defineHook, getWritable } from "workflow";

const messageHook = defineHook(z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string()
}));

export async function chatSessionWorkflow(sessionId: string) {
  "use workflow";

  const messages: UIMessage[] = [];
  const writable = getWritable();

  for await (const newMessage of messageHook.create({
    token: `session:${sessionId}`
  })) {
    messages.push(newMessage);

    const agent = new DurableAgent({ /* config */ });
    const result = await agent.stream({ messages, writable });

    messages.push(...result.messages);
  }
}

// API routes
// POST /api/chat - Start session
// POST /api/chat/[id] - Send message via hook
```

**When to use:**
| Pattern | Use When |
|---------|----------|
| Single-Turn | Adapting existing chat systems, simple Q&A |
| Multi-Turn | Production apps, need full session observability, backend message injection |

---

### Fan-Out / Fan-In (Parallel Processing)

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
  // Process individual item
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

### Saga Pattern (Compensating Transactions)

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

### Circuit Breaker Pattern

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

### Scheduled / Recurring Workflows

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

### Human-in-the-Loop

```typescript
export async function contentModerationWorkflow(contentId: string) {
  "use workflow";

  const analysis = await analyzeContent(contentId);

  if (analysis.confidence < 0.9) {
    // Create approval hook
    const approvalHook = createHook<{
      approved: boolean;
      reason?: string;
    }>();

    // Notify moderator
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
```

---

## Debugging Workflows

### Observability Tools

```bash
# Web UI - Visual workflow explorer
npx workflow web

# CLI - List recent runs
npx workflow inspect runs

# CLI - Detailed run info
npx workflow inspect run <run-id>

# CLI - List steps for a run
npx workflow inspect steps <run-id>

# Inspect production (Vercel)
npx workflow inspect runs --backend vercel --env production
```

---

### Logging Best Practices

```typescript
import { getWorkflowMetadata, getStepMetadata } from "workflow";

export async function debuggableWorkflow(input: unknown) {
  "use workflow";

  const { workflowRunId } = getWorkflowMetadata();
  console.log(`[${workflowRunId}] Workflow started with:`, input);

  const result = await someStep(input);

  console.log(`[${workflowRunId}] Workflow completed:`, result);
  return result;
}

async function someStep(input: unknown) {
  "use step";

  const { stepId } = getStepMetadata();
  console.log(`[Step ${stepId}] Processing:`, input);

  // ... work

  console.log(`[Step ${stepId}] Complete`);
  return result;
}
```

---

### Common Errors & Solutions

#### "Cannot use Node.js module in workflow functions"

**Problem:** Using `fs`, `path`, `crypto`, etc. in workflow context.

**Solution:** Move to step function.

```typescript
// BAD
export async function workflow() {
  "use workflow";
  const data = fs.readFileSync("file.txt"); // Error!
}

// GOOD
export async function workflow() {
  "use workflow";
  const data = await readFile("file.txt");
}

async function readFile(path: string) {
  "use step";
  return fs.readFileSync(path, "utf-8");
}
```

---

#### "fetch-in-workflow" Error

**Problem:** Using global `fetch` in workflow context.

**Solution:** Use workflow's `fetch` or move to step.

```typescript
// BAD
export async function workflow() {
  "use workflow";
  const res = await globalThis.fetch(url); // Error!
}

// GOOD - Option 1: Use workflow fetch
import { fetch } from "workflow";

export async function workflow() {
  "use workflow";
  const res = await fetch(url); // Works!
}

// GOOD - Option 2: Use step
export async function workflow() {
  "use workflow";
  const data = await fetchData(url);
}

async function fetchData(url: string) {
  "use step";
  const res = await fetch(url);
  return res.json();
}
```

---

#### "serialization-failed" Error

**Problem:** Passing non-serializable data between workflow/steps.

**Solution:** Ensure all data is serializable.

```typescript
// BAD - Functions aren't serializable
const callback = () => console.log("hi");
await someStep(callback); // Error!

// BAD - Circular references
const obj: any = {};
obj.self = obj;
await someStep(obj); // Error!

// GOOD - Use serializable types
await someStep({
  id: "123",
  date: new Date(),
  items: ["a", "b", "c"],
  config: new Map([["key", "value"]])
});
```

---

#### "webhook-response-not-sent" Error

**Problem:** Webhook didn't send response before step completed.

**Solution:** Call `respondWith()` in the step.

```typescript
// BAD
async function handleWebhook(request: RequestWithResponse) {
  "use step";
  const data = await request.json();
  // Forgot to respond!
}

// GOOD
async function handleWebhook(request: RequestWithResponse) {
  "use step";
  const data = await request.json();

  // Always respond
  request.respondWith(
    Response.json({ received: true })
  );

  return data;
}
```

---

#### Workflow Seems Stuck

**Check:**
1. Is a step throwing errors and retrying indefinitely?
2. Is there an infinite loop without sleep?
3. Is a hook/webhook never being resumed?

**Debug:**
```bash
# Check run status
npx workflow inspect run <run-id>

# Check step status
npx workflow inspect steps <run-id>

# Look for error logs in your app's console output
```

---

### Testing Workflows

#### Unit Testing Steps

```typescript
import { describe, it, expect, vi } from "vitest";

// Steps are just functions - test normally
describe("createUser step", () => {
  it("should create user with valid email", async () => {
    const mockDB = vi.fn().mockResolvedValue({ id: "123" });

    const result = await createUserStep("test@example.com", mockDB);

    expect(result.id).toBe("123");
    expect(mockDB).toHaveBeenCalledWith("test@example.com");
  });
});
```

#### Integration Testing

```typescript
import { start, getRun } from "workflow/api";

describe("userSignupWorkflow", () => {
  it("should complete signup flow", async () => {
    const run = await start(userSignupWorkflow, ["test@example.com"]);

    // Wait for completion (with timeout)
    const status = await Promise.race([
      run.status,
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error("Timeout")), 30000)
      )
    ]);

    expect(status).toBe("completed");
  });
});
```

---

### Performance Tips

1. **Batch steps when possible:**
```typescript
// Slow - 100 sequential steps
for (const item of items) {
  await processItem(item);
}

// Fast - Parallel execution
await Promise.all(items.map(item => processItem(item)));
```

2. **Use streaming for large data:**
```typescript
// Don't load everything into memory
const writable = getWritable();
for await (const chunk of largeDataSource) {
  await writeChunk(writable, chunk);
}
```

3. **Minimize step granularity:**
```typescript
// Too granular - unnecessary overhead
await step1(); await step2(); await step3();

// Better - combine related operations
await combinedStep();
```

4. **Use appropriate sleep durations:**
```typescript
// Polling too frequently
while (!ready) {
  await sleep("1s");  // 86,400 requests/day
  ready = await checkStatus();
}

// Better - exponential backoff
let delay = 1000;
while (!ready) {
  await sleep(delay);
  delay = Math.min(delay * 2, 60000);
  ready = await checkStatus();
}
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKFLOW_TARGET_WORLD` | World implementation package | Auto-detected |
| `WORKFLOW_LOG_LEVEL` | Logging verbosity | `info` |

### Middleware Configuration

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Your middleware logic
  return NextResponse.next();
}

// Exclude workflow routes from middleware
export const config = {
  matcher: [
    // Match all routes except workflow internals
    "/((?!.well-known/workflow|_next/static|_next/image|favicon.ico).*)"
  ]
};
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "plugins": [
      { "name": "workflow/ts-plugin" }
    ],
    "moduleResolution": "bundler",
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  }
}
```
