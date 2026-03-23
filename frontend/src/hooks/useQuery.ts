import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listConversations,
  getConversation,
  listMessages,
  listNamespaces,
  listEvalRuns,
  getEvalRun,
  listEvalSamples,
  createConversation,
  deleteConversation,
  queryRAG,
} from "@/lib/api";

// ── Conversation queries ────────────────────────────────────────────

export function useConversations(namespaceId?: string) {
  return useQuery({
    queryKey: ["conversations", namespaceId],
    queryFn: () => listConversations(namespaceId),
  });
}

export function useConversation(convId: string | undefined) {
  return useQuery({
    queryKey: ["conversation", convId],
    queryFn: () => getConversation(convId!),
    enabled: !!convId,
  });
}

export function useMessages(convId: string | undefined) {
  return useQuery({
    queryKey: ["messages", convId],
    queryFn: () => listMessages(convId!),
    enabled: !!convId,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ namespaceId, title }: { namespaceId: string; title?: string }) =>
      createConversation(namespaceId, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}

// ── Namespace queries ───────────────────────────────────────────────

export function useNamespaces() {
  return useQuery({
    queryKey: ["namespaces"],
    queryFn: listNamespaces,
  });
}

// ── Eval queries ────────────────────────────────────────────────────

export function useEvalRuns(namespaceId?: string) {
  return useQuery({
    queryKey: ["eval-runs", namespaceId],
    queryFn: () => listEvalRuns(namespaceId),
  });
}

export function useEvalRun(runId: string | undefined) {
  return useQuery({
    queryKey: ["eval-run", runId],
    queryFn: () => getEvalRun(runId!),
    enabled: !!runId,
  });
}

export function useEvalSamples(runId: string | undefined) {
  return useQuery({
    queryKey: ["eval-samples", runId],
    queryFn: () => listEvalSamples(runId!),
    enabled: !!runId,
  });
}

// ── Query mutation (non-streaming fallback) ─────────────────────────

export function useRAGQuery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      conversationId,
      query,
      namespaceId,
    }: {
      conversationId: string;
      query: string;
      namespaceId?: string;
    }) => queryRAG(conversationId, query, namespaceId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["messages", variables.conversationId],
      });
    },
  });
}
