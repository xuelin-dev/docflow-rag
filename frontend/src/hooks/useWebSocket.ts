import { useCallback, useRef, useState } from "react";
import { DocFlowWebSocket, type WSEventHandler } from "@/lib/ws";
import type { Source } from "@/lib/types";

interface UseWebSocketReturn {
  isConnected: boolean;
  isStreaming: boolean;
  streamingContent: string;
  streamingSources: Source[];
  sendQuery: (conversationId: string, query: string, namespaceId?: string) => void;
  cancel: () => void;
}

/**
 * Hook wrapping DocFlowWebSocket for streaming RAG responses.
 * Manages connection lifecycle and exposes streaming state.
 */
export function useWebSocket(
  onDone?: (messageId: string, content: string, sources: Source[]) => void,
  onError?: (error: string) => void
): UseWebSocketReturn {
  const wsRef = useRef<DocFlowWebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingSources, setStreamingSources] = useState<Source[]>([]);

  const contentRef = useRef("");
  const sourcesRef = useRef<Source[]>([]);

  const sendQuery = useCallback(
    (conversationId: string, query: string, namespaceId?: string) => {
      // Close existing connection
      wsRef.current?.close();

      setStreamingContent("");
      setStreamingSources([]);
      contentRef.current = "";
      sourcesRef.current = [];

      const handlers: WSEventHandler = {
        onToken: (token) => {
          contentRef.current += token;
          setStreamingContent(contentRef.current);
        },
        onSources: (sources) => {
          sourcesRef.current = sources;
          setStreamingSources(sources);
        },
        onDone: (messageId) => {
          setIsStreaming(false);
          setIsConnected(false);
          onDone?.(messageId, contentRef.current, sourcesRef.current);
        },
        onError: (error) => {
          setIsStreaming(false);
          setIsConnected(false);
          onError?.(error);
        },
        onOpen: () => {
          setIsConnected(true);
          setIsStreaming(true);
        },
        onClose: () => {
          setIsConnected(false);
        },
      };

      wsRef.current = new DocFlowWebSocket(handlers);
      wsRef.current.connect(conversationId, query, namespaceId);
    },
    [onDone, onError]
  );

  const cancel = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setIsStreaming(false);
    setIsConnected(false);
  }, []);

  return {
    isConnected,
    isStreaming,
    streamingContent,
    streamingSources,
    sendQuery,
    cancel,
  };
}
