import { create } from "zustand";
import type { Conversation, Message, Source } from "@/lib/types";
import {
  listConversations,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation,
  listMessages,
} from "@/lib/api";
import { DocFlowWebSocket } from "@/lib/ws";

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Map<string, Message[]>;
  isStreaming: boolean;
  streamingContent: string;
  streamingSources: Source[];

  // Actions
  loadConversations: (namespaceId?: string) => Promise<void>;
  setActiveConversation: (convId: string) => Promise<void>;
  createConversation: (namespaceId: string, title?: string) => Promise<Conversation>;
  deleteConversation: (convId: string) => Promise<void>;
  sendQuery: (query: string, namespaceId?: string) => void;
  cancelStream: () => void;
}

let activeWs: DocFlowWebSocket | null = null;

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  messages: new Map(),
  isStreaming: false,
  streamingContent: "",
  streamingSources: [],

  loadConversations: async (namespaceId) => {
    const conversations = await listConversations(namespaceId);
    set({ conversations });
  },

  setActiveConversation: async (convId) => {
    set({ activeConversationId: convId });
    // Load messages if not cached
    if (!get().messages.has(convId)) {
      const msgs = await listMessages(convId);
      set((state) => {
        const newMap = new Map(state.messages);
        newMap.set(convId, msgs);
        return { messages: newMap };
      });
    }
  },

  createConversation: async (namespaceId, title) => {
    const conv = await apiCreateConversation(namespaceId, title);
    set((state) => ({
      conversations: [conv, ...state.conversations],
      activeConversationId: conv.id,
    }));
    return conv;
  },

  deleteConversation: async (convId) => {
    await apiDeleteConversation(convId);
    set((state) => {
      const newMessages = new Map(state.messages);
      newMessages.delete(convId);
      return {
        conversations: state.conversations.filter((c) => c.id !== convId),
        messages: newMessages,
        activeConversationId:
          state.activeConversationId === convId ? null : state.activeConversationId,
      };
    });
  },

  sendQuery: (query, namespaceId) => {
    const { activeConversationId } = get();
    if (!activeConversationId) return;

    // Add user message optimistically
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId,
      role: "user",
      content: query,
      sources: [],
      created_at: new Date().toISOString(),
    };

    set((state) => {
      const newMap = new Map(state.messages);
      const existing = newMap.get(activeConversationId) ?? [];
      newMap.set(activeConversationId, [...existing, userMsg]);
      return {
        messages: newMap,
        isStreaming: true,
        streamingContent: "",
        streamingSources: [],
      };
    });

    // Open WebSocket for streaming
    activeWs = new DocFlowWebSocket({
      onToken: (token) => {
        set((state) => ({
          streamingContent: state.streamingContent + token,
        }));
      },
      onSources: (sources) => {
        set({ streamingSources: sources });
      },
      onDone: (messageId) => {
        const state = get();
        const assistantMsg: Message = {
          id: messageId,
          conversation_id: activeConversationId,
          role: "assistant",
          content: state.streamingContent,
          sources: state.streamingSources,
          created_at: new Date().toISOString(),
        };
        const newMap = new Map(state.messages);
        const existing = newMap.get(activeConversationId) ?? [];
        newMap.set(activeConversationId, [...existing, assistantMsg]);
        set({
          messages: newMap,
          isStreaming: false,
          streamingContent: "",
          streamingSources: [],
        });
        activeWs = null;
      },
      onError: (error) => {
        console.error("[Chat] Stream error:", error);
        set({ isStreaming: false, streamingContent: "", streamingSources: [] });
        activeWs = null;
      },
    });

    activeWs.connect(activeConversationId, query, namespaceId);
  },

  cancelStream: () => {
    activeWs?.close();
    activeWs = null;
    set({ isStreaming: false, streamingContent: "", streamingSources: [] });
  },
}));
