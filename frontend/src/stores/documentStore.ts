import { create } from "zustand";
import type { Document } from "@/lib/types";
import {
  listDocuments,
  uploadDocument as apiUploadDocument,
  deleteDocument as apiDeleteDocument,
} from "@/lib/api";

interface DocumentState {
  documents: Document[];
  isLoading: boolean;
  uploadProgress: Map<string, number>;

  // Actions
  refreshDocuments: (namespaceId?: string) => Promise<void>;
  uploadDocument: (namespaceId: string, file: File) => Promise<void>;
  deleteDocument: (docId: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  isLoading: false,
  uploadProgress: new Map(),

  refreshDocuments: async (namespaceId) => {
    set({ isLoading: true });
    try {
      const result = await listDocuments(namespaceId);
      set({ documents: result.items });
    } finally {
      set({ isLoading: false });
    }
  },

  uploadDocument: async (namespaceId, file) => {
    const fileKey = file.name;
    set((state) => {
      const newProgress = new Map(state.uploadProgress);
      newProgress.set(fileKey, 0);
      return { uploadProgress: newProgress };
    });

    try {
      const doc = await apiUploadDocument(namespaceId, file, (pct) => {
        set((state) => {
          const newProgress = new Map(state.uploadProgress);
          newProgress.set(fileKey, pct);
          return { uploadProgress: newProgress };
        });
      });

      set((state) => {
        const newProgress = new Map(state.uploadProgress);
        newProgress.delete(fileKey);
        return {
          documents: [doc, ...state.documents],
          uploadProgress: newProgress,
        };
      });
    } catch (error) {
      set((state) => {
        const newProgress = new Map(state.uploadProgress);
        newProgress.delete(fileKey);
        return { uploadProgress: newProgress };
      });
      throw error;
    }
  },

  deleteDocument: async (docId) => {
    await apiDeleteDocument(docId);
    set((state) => ({
      documents: state.documents.filter((d) => d.id !== docId),
    }));
  },
}));
