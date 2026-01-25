# Workflow DevKit Debugging Guide

## Table of Contents

1. [Observability Tools](#observability-tools)
2. [Error Reference](#error-reference)
3. [Logging Best Practices](#logging-best-practices)
4. [Testing Workflows](#testing-workflows)
5. [Performance Tips](#performance-tips)
6. [Configuration Issues](#configuration-issues)

---

## Observability Tools

### CLI Commands

```bash
# Web UI - Visual workflow explorer
npx workflow web

# List recent runs
npx workflow inspect runs

# Detailed run information
npx workflow inspect run <run-id>

# List steps for a run
npx workflow inspect steps <run-id>

# Get help
npx workflow inspect --help
```

### Inspecting Production (Vercel)

```bash
# Ensure Vercel CLI is authenticated and project is linked
npx workflow inspect runs --backend vercel
npx workflow inspect runs --backend vercel --env production
npx workflow inspect runs --backend vercel --env preview
```

### Debugging a Stuck Workflow

1. Check run status: `npx workflow inspect run <run-id>`
2. Check step status: `npx workflow inspect steps <run-id>`
3. Look for:
   - Steps throwing errors and retrying indefinitely
   - Infinite loops without sleep
   - Hooks/webhooks never being resumed

---

## Error Reference

### fetch-in-workflow

**Error:** `Global 'fetch' is unavailable in workflow functions.`

**Cause:** Using `fetch()` directly in workflows, or libraries (like AI SDK) that call fetch internally.

**Solution:**

```typescript
// BAD - Direct fetch in workflow
export async function workflow() {
  "use workflow";
  const res = await fetch(url); // Error!
}

// GOOD - Option 1: Use workflow's fetch
import { fetch } from "workflow";

export async function workflow() {
  "use workflow";
  const res = await fetch(url); // Works!
}

// GOOD - Option 2: Move to step
async function fetchData(url: string) {
  "use step";
  const res = await fetch(url);
  return res.json();
}

// GOOD - Option 3: For AI SDK / libraries that use fetch internally
import { fetch } from "workflow";

export async function chatWorkflow(messages: UIMessage[]) {
  "use workflow";
  globalThis.fetch = fetch; // Enable fetch for libraries

  const result = await generateText({
    model: openai("gpt-4"),
    prompt: "Hello"
  });
}
```

---

### node-js-module-in-workflow

**Error:** `Cannot use Node.js module "fs" in workflow functions. Move this module to a step function.`

**Cause:** Using Node.js core modules in workflow context.

**Restricted modules:** `fs`, `path`, `http`, `https`, `net`, `dns`, `child_process`, `cluster`, `crypto`, `os`, `stream`

**Solution:**

```typescript
import * as fs from "fs";

// BAD
export async function workflow(filePath: string) {
  "use workflow";
  const content = fs.readFileSync(filePath); // Error!
}

// GOOD
export async function workflow(filePath: string) {
  "use workflow";
  const content = await readFile(filePath);
}

async function readFile(filePath: string) {
  "use step";
  return fs.readFileSync(filePath, "utf-8"); // OK in step
}
```

**Alternative:** Use Web Platform APIs (Web Crypto, Web Streams) directly in workflows.

---

### timeout-in-workflow

**Error:** `Timeout functions like 'setTimeout' and 'setInterval' are not supported in workflow functions.`

**Cause:** Using JavaScript timing functions which break deterministic replay.

**Prohibited:** `setTimeout`, `clearTimeout`, `setInterval`, `clearInterval`, `setImmediate`, `clearImmediate`

**Solution:**

```typescript
// BAD
await new Promise(resolve => setTimeout(resolve, 5000));

// GOOD
import { sleep } from "workflow";
await sleep("5s");
```

---

### serialization-failed

**Error:** `Failed to serialize workflow arguments. Ensure you're passing serializable types.`

**Cause:** Passing non-serializable data between workflow/step boundaries.

**Supported types:**
- JSON types: string, number, boolean, null, arrays, objects
- Extended: `undefined`, `bigint`, `Date`, `RegExp`, `URL`
- Collections: `Map`, `Set`, `ArrayBuffer`, typed arrays
- Web APIs: `Headers`, `Request`, `Response`
- Streams: `ReadableStream`, `WritableStream`

**NOT supported:**
- Functions
- Class instances (convert to plain objects)
- Symbols
- Circular references

**Solution:**

```typescript
// BAD - Functions aren't serializable
const callback = () => console.log("hi");
await someStep(callback); // Error!

// BAD - Circular references
const obj: any = {};
obj.self = obj;
await someStep(obj); // Error!

// GOOD - Plain objects
await someStep({
  id: "123",
  date: new Date(),
  items: ["a", "b"],
  config: new Map([["key", "value"]])
});

// BAD - Class instance
await someStep(new MyClass());

// GOOD - Convert to plain object
await someStep({ ...myClassInstance });
```

---

### hook-conflict

**Error:** `Hook token conflict: Hook with token <token> already exists for this project.`

**Cause:** Multiple workflow runs using the same hook token simultaneously.

**Solution:**

```typescript
// BAD - Hardcoded token
const hook = createHook({ token: "payment-hook" });

// GOOD - Include unique identifier
const hook = createHook({ token: `payment:${orderId}` });

// GOOD - Let runtime auto-generate
const hook = createHook(); // Unique token generated
```

**Handling conflicts:**

```typescript
try {
  const hook = createHook({ token: `order:${orderId}` });
} catch (error) {
  if (error instanceof WorkflowRuntimeError && error.slug === "hook-conflict") {
    // Handle duplicate - maybe workflow already processing this order
  }
}
```

**Token lifecycle:** Tokens release when workflow completes, fails, or is cancelled.

---

### webhook-response-not-sent

**Error:** Webhook didn't send response before step completed.

**Cause:** Forgetting to call `respondWith()` in webhook handler.

**Solution:**

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

  request.respondWith(
    Response.json({ received: true })
  );

  return data;
}
```

---

### webhook-invalid-respond-with-value

**Error:** Invalid value passed to `respondWith()`.

**Solution:** Pass a valid `Response` object:

```typescript
// BAD
request.respondWith("success");

// GOOD
request.respondWith(Response.json({ success: true }));
request.respondWith(new Response("OK", { status: 200 }));
```

---

### start-invalid-workflow-function

**Error:** Invalid workflow function passed to `start()`.

**Cause:** Function doesn't have `"use workflow"` directive or isn't exported.

**Solution:**

```typescript
// BAD - Missing directive
export async function myWorkflow() {
  await doSomething();
}

// GOOD
export async function myWorkflow() {
  "use workflow";
  await doSomething();
}

// BAD - Not exported
async function myWorkflow() {
  "use workflow";
}

// GOOD
export async function myWorkflow() {
  "use workflow";
}
```

---

### Next.js 16.1+ Compatibility

**Error:** `Cannot find module 'next/dist/lib/server-external-packages.json'`

**Solution:**

```bash
npm install workflow@latest
# or specifically
npm install workflow@4.0.1-beta.26
```

---

## Logging Best Practices

```typescript
import { getWorkflowMetadata, getStepMetadata } from "workflow";

export async function debuggableWorkflow(input: unknown) {
  "use workflow";

  const { workflowRunId } = getWorkflowMetadata();
  console.log(`[${workflowRunId}] Workflow started:`, input);

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

## Testing Workflows

### Unit Testing Steps

Steps are just functions - test them normally:

```typescript
import { describe, it, expect, vi } from "vitest";

describe("createUser step", () => {
  it("creates user with valid email", async () => {
    const mockDB = vi.fn().mockResolvedValue({ id: "123" });

    const result = await createUserStep("test@example.com", mockDB);

    expect(result.id).toBe("123");
    expect(mockDB).toHaveBeenCalledWith("test@example.com");
  });
});
```

### Integration Testing

```typescript
import { start } from "workflow/api";

describe("userSignupWorkflow", () => {
  it("completes signup flow", async () => {
    const run = await start(userSignupWorkflow, ["test@example.com"]);

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

## Performance Tips

### 1. Use Parallel Execution

```typescript
// SLOW - 100 sequential steps
for (const item of items) {
  await processItem(item);
}

// FAST - Parallel
await Promise.all(items.map(item => processItem(item)));
```

### 2. Minimize Step Granularity

```typescript
// TOO GRANULAR - Unnecessary overhead
await step1();
await step2();
await step3();

// BETTER - Combine related operations
await combinedStep();
```

### 3. Use Streaming for Large Data

```typescript
const writable = getWritable();
for await (const chunk of largeDataSource) {
  await writeChunk(writable, chunk);
}
```

### 4. Use Exponential Backoff for Polling

```typescript
// TOO FREQUENT - 86,400 requests/day
while (!ready) {
  await sleep("1s");
  ready = await checkStatus();
}

// BETTER - Exponential backoff
let delay = 1000;
while (!ready) {
  await sleep(delay);
  delay = Math.min(delay * 2, 60000); // Max 1 minute
  ready = await checkStatus();
}
```

---

## Configuration Issues

### Middleware Blocking Workflows

If using Next.js middleware, exclude workflow paths:

```typescript
// middleware.ts
export const config = {
  matcher: [
    "/((?!.well-known/workflow|_next/static|_next/image|favicon.ico).*)"
  ]
};
```

### TypeScript IntelliSense

Add to `tsconfig.json`:

```json
{
  "compilerOptions": {
    "plugins": [{ "name": "workflow/ts-plugin" }]
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKFLOW_TARGET_WORLD` | World implementation package | Auto-detected |
| `WORKFLOW_LOG_LEVEL` | Logging verbosity | `info` |
