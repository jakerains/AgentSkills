import { NextjsCodexSidecar } from "../../../../lib/codex-app-server.js";

export async function POST(request: Request): Promise<Response> {
  const { prompt } = (await request.json()) as { prompt: string };

  const streamedEvents: unknown[] = [];
  const sidecar = new NextjsCodexSidecar((message) => {
    streamedEvents.push(message);
  });

  await sidecar.initialize();

  const account = await sidecar.request<{
    requiresOpenaiAuth: boolean;
    account: unknown;
  }>("account/read", {
    refreshToken: false,
  });

  const thread = await sidecar.request<{ thread: { id: string } }>("thread/start", {
    model: "gpt-5.4",
  });

  await sidecar.request("turn/start", {
    threadId: thread.thread.id,
    input: [{ type: "text", text: prompt }],
  });

  return Response.json({
    account,
    threadId: thread.thread.id,
    note: "For a real app, stream normalized notifications to the browser instead of buffering them in memory.",
    bufferedEvents: streamedEvents,
  });
}
