import { spawn, type ChildProcessByStdio } from "node:child_process";
import readline from "node:readline";
import type { Readable, Writable } from "node:stream";

export type JsonRpcError = {
  code: number;
  message: string;
  data?: unknown;
};

export type JsonRpcRequest = {
  id: number;
  method: string;
  params?: unknown;
};

export type JsonRpcNotification = {
  method: string;
  params?: unknown;
};

export type JsonRpcResponse<T> =
  | { id: number; result: T }
  | { id: number; error: JsonRpcError };

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
};

export class CodexAppServerClient {
  private readonly proc: ChildProcessByStdio<Writable, Readable, null>;
  private readonly pending = new Map<number, PendingRequest>();
  private nextId = 1;

  onNotification?: (message: JsonRpcNotification) => void;
  onServerRequest?: (message: JsonRpcRequest) => void | Promise<void>;

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
    this.proc.stdin.write(`${JSON.stringify({ method, params })}\n`);
  }

  respond(id: number, result: unknown): void {
    this.proc.stdin.write(`${JSON.stringify({ id, result })}\n`);
  }

  respondWithError(id: number, error: JsonRpcError): void {
    this.proc.stdin.write(`${JSON.stringify({ id, error })}\n`);
  }

  async initialize(clientInfo: {
    name: string;
    title: string;
    version: string;
  }): Promise<void> {
    await this.request("initialize", {
      clientInfo,
      capabilities: {
        experimentalApi: true,
      },
    });
    this.notify("initialized", {});
  }

  close(): void {
    this.proc.kill();
  }

  private async handleLine(line: string): Promise<void> {
    const message = JSON.parse(line) as
      | JsonRpcRequest
      | JsonRpcNotification
      | JsonRpcResponse<unknown>;

    if ("id" in message && !("method" in message)) {
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

    if ("id" in message && "method" in message) {
      await this.onServerRequest?.(message);
      return;
    }

    this.onNotification?.(message);
  }
}
