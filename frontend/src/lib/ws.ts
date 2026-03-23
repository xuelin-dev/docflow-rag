import type { WSMessage, Source } from "./types";

export type WSEventHandler = {
  onToken: (token: string) => void;
  onSources: (sources: Source[]) => void;
  onDone: (messageId: string) => void;
  onError: (error: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
};

/**
 * WebSocket client for streaming RAG query responses.
 * Each instance manages a single connection for one query stream.
 */
export class DocFlowWebSocket {
  private ws: WebSocket | null = null;
  private handlers: WSEventHandler;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor(handlers: WSEventHandler) {
    this.handlers = handlers;
  }

  /** Connect to the streaming endpoint and send a query */
  connect(conversationId: string, query: string, namespaceId?: string): void {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/query`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.handlers.onOpen?.();

      // Send query payload once connected
      this.ws?.send(
        JSON.stringify({
          conversation_id: conversationId,
          query,
          namespace_id: namespaceId,
          stream: true,
        })
      );
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSMessage = JSON.parse(event.data as string);

        switch (msg.type) {
          case "token":
            this.handlers.onToken(msg.data as string);
            break;
          case "sources":
            this.handlers.onSources(msg.data as Source[]);
            break;
          case "done": {
            const { message_id } = msg.data as { message_id: string };
            this.handlers.onDone(message_id);
            this.close();
            break;
          }
          case "error": {
            const { error } = msg.data as { error: string };
            this.handlers.onError(error);
            this.close();
            break;
          }
        }
      } catch {
        console.error("[WS] Failed to parse message:", event.data);
      }
    };

    this.ws.onerror = () => {
      console.error("[WS] Connection error");
    };

    this.ws.onclose = (event) => {
      this.handlers.onClose?.();

      // Auto-reconnect on abnormal closure
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 10_000);
        console.warn(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(conversationId, query, namespaceId), delay);
      }
    };
  }

  /** Close the WebSocket connection */
  close(): void {
    if (this.ws) {
      this.ws.onclose = null; // prevent reconnect on intentional close
      this.ws.close();
      this.ws = null;
    }
  }

  /** Check if the connection is open */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
