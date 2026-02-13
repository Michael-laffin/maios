import { create } from "zustand";

interface UIStore {
  sidebarOpen: boolean;
  selectedAgentId: string | null;
  selectedProjectId: string | null;
  viewMode: "dashboard" | "neural" | "timeline";
  commandPaletteOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  setSelectedAgentId: (id: string | null) => void;
  setSelectedProjectId: (id: string | null) => void;
  setViewMode: (mode: "dashboard" | "neural" | "timeline") => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  selectedAgentId: null,
  selectedProjectId: null,
  viewMode: "dashboard",
  commandPaletteOpen: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
}));
