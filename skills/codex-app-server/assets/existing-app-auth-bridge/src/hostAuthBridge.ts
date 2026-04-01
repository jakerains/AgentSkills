import {
  CodexAppServerClient,
  type JsonRpcNotification,
  type JsonRpcRequest,
} from "./client.js";

export type ChatGPTTokens = {
  idToken: string;
  accessToken: string;
};

export type HostAuthBridgeOptions = {
  openExternalUrl: (url: string) => Promise<void> | void;
  getFreshChatGPTTokens?: (context: {
    reason: string;
    previousAccountId?: string;
  }) => Promise<ChatGPTTokens>;
  onAccountUpdated?: (authMode: string | null) => void;
  onLoginCompleted?: (payload: {
    loginId: string | null;
    success: boolean;
    error: string | null;
  }) => void;
  onRateLimitsUpdated?: (payload: unknown) => void;
};

export class CodexHostAuthBridge {
  constructor(
    private readonly client: CodexAppServerClient,
    private readonly options: HostAuthBridgeOptions,
  ) {
    this.client.onNotification = (message) => {
      this.handleNotification(message);
    };

    this.client.onServerRequest = async (message) => {
      await this.handleServerRequest(message);
    };
  }

  async readAccount(refreshToken = false): Promise<unknown> {
    return await this.client.request("account/read", { refreshToken });
  }

  async loginWithApiKey(apiKey: string): Promise<void> {
    await this.client.request("account/login/start", {
      type: "apiKey",
      apiKey,
    });
  }

  async loginWithManagedChatGPT(): Promise<{ loginId: string; authUrl: string }> {
    const result = await this.client.request<{
      type: "chatgpt";
      loginId: string;
      authUrl: string;
    }>("account/login/start", {
      type: "chatgpt",
    });

    await this.options.openExternalUrl(result.authUrl);
    return { loginId: result.loginId, authUrl: result.authUrl };
  }

  async loginWithExternalTokens(tokens: ChatGPTTokens): Promise<void> {
    await this.client.request("account/login/start", {
      type: "chatgptAuthTokens",
      idToken: tokens.idToken,
      accessToken: tokens.accessToken,
    });
  }

  async logout(): Promise<void> {
    await this.client.request("account/logout");
  }

  async readRateLimits(): Promise<unknown> {
    return await this.client.request("account/rateLimits/read");
  }

  private handleNotification(message: JsonRpcNotification): void {
    if (message.method === "account/updated") {
      const params = (message.params ?? {}) as { authMode?: string | null };
      this.options.onAccountUpdated?.(params.authMode ?? null);
      return;
    }

    if (message.method === "account/login/completed") {
      const params = (message.params ?? {}) as {
        loginId: string | null;
        success: boolean;
        error: string | null;
      };
      this.options.onLoginCompleted?.(params);
      return;
    }

    if (message.method === "account/rateLimits/updated") {
      this.options.onRateLimitsUpdated?.(message.params);
    }
  }

  private async handleServerRequest(message: JsonRpcRequest): Promise<void> {
    if (message.method !== "account/chatgptAuthTokens/refresh") {
      this.client.respondWithError(message.id, {
        code: -32601,
        message: `Unsupported server request: ${message.method}`,
      });
      return;
    }

    if (!this.options.getFreshChatGPTTokens) {
      this.client.respondWithError(message.id, {
        code: -32000,
        message: "Host did not provide a ChatGPT token refresh callback",
      });
      return;
    }

    try {
      const params = (message.params ?? {}) as {
        reason?: string;
        previousAccountId?: string;
      };
      const tokens = await this.options.getFreshChatGPTTokens({
        reason: params.reason ?? "unknown",
        previousAccountId: params.previousAccountId,
      });
      this.client.respond(message.id, tokens);
    } catch (error) {
      this.client.respondWithError(message.id, {
        code: -32000,
        message:
          error instanceof Error ? error.message : "Failed to refresh ChatGPT tokens",
      });
    }
  }
}
