export type CodexRendererApi = {
  startThread: (model?: string) => Promise<unknown>;
  startTurn: (threadId: string, text: string) => Promise<unknown>;
};

// Sketch:
// contextBridge.exposeInMainWorld("codex", {
//   startThread: (model?: string) => ipcRenderer.invoke("codex:thread:start", { model }),
//   startTurn: (threadId: string, text: string) =>
//     ipcRenderer.invoke("codex:turn:start", {
//       threadId,
//       input: [{ type: "text", text }],
//     }),
// } satisfies CodexRendererApi);
