import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listDocuments,
  getDocument,
  uploadDocument,
  deleteDocument,
  listChunks,
} from "@/lib/api";
import type { Document, Chunk, PaginatedResponse } from "@/lib/types";

/** Fetch paginated document list */
export function useDocuments(namespaceId?: string, page = 1, pageSize = 20) {
  return useQuery<PaginatedResponse<Document>>({
    queryKey: ["documents", namespaceId, page, pageSize],
    queryFn: () => listDocuments(namespaceId, page, pageSize),
  });
}

/** Fetch a single document */
export function useDocument(docId: string | undefined) {
  return useQuery<Document>({
    queryKey: ["document", docId],
    queryFn: () => getDocument(docId!),
    enabled: !!docId,
  });
}

/** Fetch chunks for a document */
export function useChunks(docId: string | undefined) {
  return useQuery<Chunk[]>({
    queryKey: ["chunks", docId],
    queryFn: () => listChunks(docId!),
    enabled: !!docId,
  });
}

/** Upload a document with progress tracking */
export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      namespaceId,
      file,
      onProgress,
    }: {
      namespaceId: string;
      file: File;
      onProgress?: (pct: number) => void;
    }) => uploadDocument(namespaceId, file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

/** Delete a document */
export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}
