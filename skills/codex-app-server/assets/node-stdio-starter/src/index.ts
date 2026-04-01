import { spawn, type ChildProcessByStdio } from "node:child_process";
import readline from "node:readline";
import type { Readable, Writable } from "node:stream";

type JsonRpcError = {
  code: number;
  message: string;
  data?: unknown;
};

type JsonRpcRequest = {
  id: number;
  method: string;
  params?: unknown;
};

type JsonRpcResponse<T> =
  | { id: number; result: T }
  | { id: number; error: JsonRpcError };

type JsonRpcNotification = {
  method: string;
  params?: unknown;
};

type ThreadStartResult = {
  thread: {
    id: string;
  };
};

class CodexAppServerClient {
  private readonly proc: ChildProcessByStdio<Writable, Readable, null>;
  private readonly pending = new Map<
    number,
    {
      resolve: (value: unknown) => void;
      reject: (error: Error) => void;
    }
  >();
  private nextId = 1;

  onNotification?: (message: JsonRpcNotification) => void;

  constructor(command = "codex", args: string[] = ["app-server"]) {
    this.proc = spawn(command, args, {
      stdio: ["pipe", "pipe", "inherit"],
    });

    const lineReader = readline.createInterface({ input: this.proc.stdout });
    lineReader.on("line", (line) => {
      void this.handleLine(line);
    });
  }

  async request<T>(method: string, params?: unknown): Promise<T> {
    const id = this.nextId++;
    const payload: JsonRpcRequest = { id, method, params };

    return await new Promise<T>((resolve, reject) => {
      this.pending.set(id, {
        resolve: (value) => resolve(value as T),
        reject,
      });
      this.proc.stdin.write(`${JSON.stringify(payload)}\n`);
    });
  }

  notify(method: string, params?: unknown): void {
    const payload: JsonRpcNotification = { method, params };
    this.proc.stdin.write(`${JSON.stringify(payload)}\n`);
  }

  close(): void {
    this.proc.kill();
  }

  private async handleLine(line: string): Promise<void> {
    const message = JSON.parse(line) as
      | JsonRpcResponse<unknown>
      | JsonRpcNotification;

    if ("id" in message) {
      const pending = this.pending.get(message.id);
      if (!pending) {
        return;
      }

      this.pending.delete(message.id);

      if ("error" in message) {
        pending.reject(
          new Error(`${message.error.code}: ${message.error.message}`),
        );
        return;
      }

      pending.resolve(message.result);
      return;
    }

    this.onNotification?.(message);
  }
}

async function main(): Promise<void> {
  const client = new CodexAppServerClient();

  client.onNotification = (message) => {
    console.log("notification:", JSON.stringify(message, null, 2));
  };

  const initializeResult = await client.request<{
    userAgent: string;
    platformFamily?: string;
    platformOs?: string;
  }>("initialize", {
    clientInfo: {
      name: "my_product",
      title: "My Product",
      version: "0.1.0",
    },
    capabilities: {
      experimentalApi: true,
    },
  });

  console.log("initialized:", initializeResult);
  client.notify("initialized", {});

  const account = await client.request<{
    account: unknown;
    requiresOpenaiAuth: boolean;
  }>("account/read", {
    refreshToken: false,
  });

  console.log("account:", account);
  console.log(
    "Tip: use assets/existing-app-auth-bridge if you need managed ChatGPT login or external token refresh handling.",
  );

  const thread = await client.request<ThreadStartResult>("thread/start", {
    model: "gpt-5.4",
  });

  console.log("thread:", thread.thread.id);

  await client.request("turn/start", {
    threadId: thread.thread.id,
    input: [
      {
        type: "text",
        text: "Summarize the current project in three bullets.",
      },
    ],
  });

  process.on("SIGINT", () => {
    client.close();
    process.exit(0);
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
