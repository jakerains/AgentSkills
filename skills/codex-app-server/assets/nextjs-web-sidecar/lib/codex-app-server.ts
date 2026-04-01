import { spawn, type ChildProcessByStdio } from "node:child_process";
import readline from "node:readline";
import type { Readable, Writable } from "node:stream";

export class NextjsCodexSidecar {
  private readonly proc: ChildProcessByStdio<Writable, Readable, null>;
  private readonly pending = new Map<
    number,
    { resolve: (value: unknown) => void; reject: (error: Error) => void }
  >();
  private nextId = 1;

  constructor(private readonly onNotification?: (message: unknown) => void) {
    this.proc = spawn("codex", ["app-server"], {
      stdio: ["pipe", "pipe", "inherit"],
    });

    const lineReader = readline.createInterface({ input: this.proc.stdout });
    lineReader.on("line", (line) => {
      const message = JSON.parse(line) as Record<string, unknown>;

      if (typeof message.id === "number" && !("method" in message)) {
        const pending = this.pending.get(message.id);
        if (!pending) {
          return;
        }
        this.pending.delete(message.id);

        if ("error" in message) {
          const error = message.error as { code?: number; message?: string };
          pending.reject(
            new Error(`${error.code ?? "unknown"}: ${error.message ?? "Unknown error"}`),
          );
          return;
        }

        pending.resolve(message.result);
        return;
      }

      this.onNotification?.(message);
    });
  }

  async initialize(): Promise<void> {
    await this.request("initialize", {
      clientInfo: {
        name: "my_nextjs_app",
        title: "My Next.js App",
        version: "0.1.0",
      },
      capabilities: {
        experimentalApi: true,
      },
    });

    this.notify("initialized", {});
  }

  async request<T>(method: string, params?: unknown): Promise<T> {
    const id = this.nextId++;
    return await new Promise<T>((resolve, reject) => {
      this.pending.set(id, {
        resolve: (value) => resolve(value as T),
        reject,
      });
      this.proc.stdin.write(`${JSON.stringify({ id, method, params })}\n`);
    });
  }

  notify(method: string, params?: unknown): void {
    this.proc.stdin.write(`${JSON.stringify({ method, params })}\n`);
  }
}

// In production, keep this bridge server-side and stream only normalized events to the browser.
