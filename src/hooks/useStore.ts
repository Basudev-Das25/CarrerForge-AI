/**
 * Global application state — Zustand store.
 * Single source of truth for all UI state.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  User,
  ProviderID,
  ResumeVersion,
  OriginalDocument,
} from "@/types";

// ── Theme ───────────────────────────────────────────────────

type Theme = "light" | "dark" | "system";

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "system") {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", prefersDark);
  } else {
    root.classList.toggle("dark", theme === "dark");
  }
}

// ── Store Interface ─────────────────────────────────────────

interface AppState {
  // User
  user: User | null;
  setUser: (user: User | null) => void;

  // Theme
  theme: Theme;
  setTheme: (theme: Theme) => void;

  // AI Provider
  activeProvider: ProviderID;
  setActiveProvider: (provider: ProviderID) => void;

  // Resumes
  currentResume: ResumeVersion | null;
  setCurrentResume: (resume: ResumeVersion | null) => void;

  // Documents
  documents: OriginalDocument[];
  setDocuments: (docs: OriginalDocument[]) => void;

  // Onboarding
  onboardingComplete: boolean;
  setOnboardingComplete: (complete: boolean) => void;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;

  // Backend connection
  backendConnected: boolean;
  setBackendConnected: (connected: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // User
      user: null,
      setUser: (user) => set({ user }),

      // Theme
      theme: "system",
      setTheme: (theme) => {
        applyTheme(theme);
        set({ theme });
      },

      // AI Provider
      activeProvider: "openai" as ProviderID,
      setActiveProvider: (activeProvider) => set({ activeProvider }),

      // Resumes
      currentResume: null,
      setCurrentResume: (currentResume) => set({ currentResume }),

      // Documents
      documents: [],
      setDocuments: (documents) => set({ documents }),

      // Onboarding
      onboardingComplete: false,
      setOnboardingComplete: (onboardingComplete) => set({ onboardingComplete }),

      // UI
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      commandPaletteOpen: false,
      setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),

      // Backend
      backendConnected: false,
      setBackendConnected: (backendConnected) => set({ backendConnected }),
    }),
    {
      name: "careerforge-app-store",
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        activeProvider: state.activeProvider,
        onboardingComplete: state.onboardingComplete,
      }),
    },
  ),
);
