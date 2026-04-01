import { CodexAppServerClient } from "./client.js";
import {
  CodexHostAuthBridge,
  type ChatGPTTokens,
} from "./hostAuthBridge.js";

async function main(): Promise<void> {
  const client = new CodexAppServerClient();
  await client.initialize({
    name: "my_existing_product",
    title: "My Existing Product",
    version: "0.1.0",
  });

  const bridge = new CodexHostAuthBridge(client, {
    openExternalUrl: async (url) => {
      console.log("Open this URL in the system browser:", url);
    },
    getFreshChatGPTTokens: async (_context): Promise<ChatGPTTokens> => {
      throw new Error(
        "Replace getFreshChatGPTTokens with your host app's ChatGPT token refresh logic.",
      );
    },
    onAccountUpdated: (authMode) => {
      console.log("account updated:", authMode);
    },
    onLoginCompleted: (payload) => {
      console.log("login completed:", payload);
    },
    onRateLimitsUpdated: (payload) => {
      console.log("rate limits updated:", payload);
    },
  });

  const account = await bridge.readAccount();
  console.log("current account:", account);

  console.log("Starting managed ChatGPT login...");
  await bridge.loginWithManagedChatGPT();

  console.log("You can also use API key or externally managed token login:");
  console.log("  await bridge.loginWithApiKey(process.env.OPENAI_API_KEY!)");
  console.log(
    "  await bridge.loginWithExternalTokens({ idToken: '...', accessToken: '...' })",
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
