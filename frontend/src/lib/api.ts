import axios, { AxiosError } from "axios";
import type {
  Document,
  Namespace,
  Conversation,
  Message,
  EvalRun,
  EvalSample,
  QueryResponse,
  PaginatedResponse,
  Chunk,
} from "./types";

/** Axios instance configured for the DocFlow RAG API */
const api = axios.create({
  baseURL: "/api/v1",
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// ── Request interceptor: attach auth token ──────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("docflow_api_key");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor: normalize errors ──────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      "An unexpected error occurred";
    console.error(`[API] ${error.config?.method?.toUpperCase()} ${error.config?.url} → ${error.response?.status}: ${message}`);
    return Promise.reject(new Error(message));
  }
);

// ── Documents ───────────────────────────────────────────────────────
export async function listDocuments(
  namespaceId?: string,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<Document>> {
  const params = { namespace_id: namespaceId, page, page_size: pageSize };
  const { data } = await api.get<PaginatedResponse<Document>>("/documents", { params });
  return data;
}

export async function getDocument(docId: string): Promise<Document> {
  const { data } = await api.get<Document>(`/documents/${docId}`);
  return data;
}

export async function uploadDocument(
  namespaceId: string,
  file: File,
  onProgress?: (pct: number) => void
): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  form.append("namespace_id", namespaceId);
  const { data } = await api.post<Document>("/documents", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
  return data;
}

export async function deleteDocument(docId: string): Promise<void> {
  await api.delete(`/documents/${docId}`);
}

export async function listChunks(docId: string): Promise<Chunk[]> {
  const { data } = await api.get<Chunk[]>(`/documents/${docId}/chunks`);
  return data;
}

// ── Namespaces ──────────────────────────────────────────────────────
export async function listNamespaces(): Promise<Namespace[]> {
  const { data } = await api.get<Namespace[]>("/namespaces");
  return data;
}

export async function createNamespace(
  payload: Pick<Namespace, "name" | "description" | "embedding_model">
): Promise<Namespace> {
  const { data } = await api.post<Namespace>("/namespaces", payload);
  return data;
}

export async function deleteNamespace(nsId: string): Promise<void> {
  await api.delete(`/namespaces/${nsId}`);
}

// ── Conversations ───────────────────────────────────────────────────
export async function listConversations(
  namespaceId?: string
): Promise<Conversation[]> {
  const params = namespaceId ? { namespace_id: namespaceId } : {};
  const { data } = await api.get<Conversation[]>("/conversations", { params });
  return data;
}

export async function getConversation(convId: string): Promise<Conversation> {
  const { data } = await api.get<Conversation>(`/conversations/${convId}`);
  return data;
}

export async function createConversation(
  namespaceId: string,
  title?: string
): Promise<Conversation> {
  const { data } = await api.post<Conversation>("/conversations", {
    namespace_id: namespaceId,
    title: title ?? "New Conversation",
  });
  return data;
}

export async function deleteConversation(convId: string): Promise<void> {
  await api.delete(`/conversations/${convId}`);
}

export async function listMessages(convId: string): Promise<Message[]> {
  const { data } = await api.get<Message[]>(`/conversations/${convId}/messages`);
  return data;
}

// ── Query (non-streaming fallback) ──────────────────────────────────
export async function queryRAG(
  conversationId: string,
  query: string,
  namespaceId?: string
): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>("/query", {
    conversation_id: conversationId,
    query,
    namespace_id: namespaceId,
  });
  return data;
}

// ── Evals ───────────────────────────────────────────────────────────
export async function listEvalRuns(
  namespaceId?: string
): Promise<EvalRun[]> {
  const params = namespaceId ? { namespace_id: namespaceId } : {};
  const { data } = await api.get<EvalRun[]>("/evals", { params });
  return data;
}

export async function getEvalRun(runId: string): Promise<EvalRun> {
  const { data } = await api.get<EvalRun>(`/evals/${runId}`);
  return data;
}

export async function listEvalSamples(runId: string): Promise<EvalSample[]> {
  const { data } = await api.get<EvalSample[]>(`/evals/${runId}/samples`);
  return data;
}

export async function createEvalRun(payload: {
  namespace_id: string;
  name: string;
  config: EvalRun["config"];
}): Promise<EvalRun> {
  const { data } = await api.post<EvalRun>("/evals", payload);
  return data;
}

export default api;
