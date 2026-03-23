/** Core domain types for DocFlow RAG */

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
}

export interface Namespace {
  id: string;
  name: string;
  description: string;
  document_count: number;
  chunk_count: number;
  embedding_model: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  namespace_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  chunk_count: number;
  status: "pending" | "processing" | "ready" | "error";
  error_message?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Chunk {
  id: string;
  document_id: string;
  content: string;
  chunk_index: number;
  token_count: number;
  embedding?: number[];
  metadata: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  title: string;
  namespace_id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Source {
  chunk_id: string;
  document_id: string;
  document_name: string;
  content: string;
  score: number;
  chunk_index: number;
  metadata: Record<string, unknown>;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources: Source[];
  model?: string;
  tokens_used?: number;
  latency_ms?: number;
  created_at: string;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  conversation_id: string;
  message_id: string;
  model: string;
  tokens_used: number;
  latency_ms: number;
}

export interface EvalSample {
  id: string;
  eval_run_id: string;
  query: string;
  expected_answer: string;
  actual_answer: string;
  retrieved_chunks: Source[];
  scores: {
    faithfulness: number;
    relevancy: number;
    correctness: number;
    context_precision: number;
  };
  latency_ms: number;
}

export interface EvalRun {
  id: string;
  namespace_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  dataset_size: number;
  completed_samples: number;
  avg_scores: {
    faithfulness: number;
    relevancy: number;
    correctness: number;
    context_precision: number;
  };
  config: {
    retriever_k: number;
    chunk_size: number;
    model: string;
  };
  started_at: string;
  completed_at?: string;
  created_at: string;
}

/** API pagination wrapper */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/** WebSocket message types */
export interface WSMessage {
  type: "token" | "sources" | "done" | "error";
  data: string | Source[] | { message_id: string } | { error: string };
}
