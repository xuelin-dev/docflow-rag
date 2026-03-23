import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "light" | "dark" | "system";
type LLMProvider = "openai" | "anthropic" | "ollama" | "custom";

interface SettingsState {
  apiKey: string;
  llmProvider: LLMProvider;
  llmModel: string;
  theme: Theme;
  retrieverK: number;
  chunkSize: number;
  ollamaUrl: string;

  // Actions
  setApiKey: (key: string) => void;
  setLlmProvider: (provider: LLMProvider) => void;
  setLlmModel: (model: string) => void;
  setTheme: (theme: Theme) => void;
  setRetrieverK: (k: number) => void;
  setChunkSize: (size: number) => void;
  setOllamaUrl: (url: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKey: "",
      llmProvider: "openai",
      llmModel: "gpt-4o",
      theme: "system",
      retrieverK: 5,
      chunkSize: 512,
      ollamaUrl: "http://localhost:11434",

      setApiKey: (apiKey) => {
        localStorage.setItem("docflow_api_key", apiKey);
        set({ apiKey });
      },
      setLlmProvider: (llmProvider) => set({ llmProvider }),
      setLlmModel: (llmModel) => set({ llmModel }),
      setTheme: (theme) => {
        // Apply theme to document
        const root = document.documentElement;
        root.classList.remove("light", "dark");
        if (theme === "system") {
          const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
          root.classList.add(systemDark ? "dark" : "light");
        } else {
          root.classList.add(theme);
        }
        set({ theme });
      },
      setRetrieverK: (retrieverK) => set({ retrieverK }),
      setChunkSize: (chunkSize) => set({ chunkSize }),
      setOllamaUrl: (ollamaUrl) => set({ ollamaUrl }),
    }),
    {
      name: "docflow-settings",
      partialize: (state) => ({
        apiKey: state.apiKey,
        llmProvider: state.llmProvider,
        llmModel: state.llmModel,
        theme: state.theme,
        retrieverK: state.retrieverK,
        chunkSize: state.chunkSize,
        ollamaUrl: state.ollamaUrl,
      }),
    }
  )
);
