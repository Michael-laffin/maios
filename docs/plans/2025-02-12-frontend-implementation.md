# MAIOS Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Next.js 15 frontend with 3D visualization for MAIOS orchestration system.

**Architecture:** Next.js App Router with React Three Fiber for 3D visualization, Zustand for client state, React Query for server state, and WebSocket for real-time updates.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS 4, ShadCN UI, React Three Fiber, Zustand, React Query, Framer Motion

---

## Task 1: Project Initialization

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/next.config.ts`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`

**Step 1: Create frontend directory and initialize Next.js project**

```bash
cd /home/vernox/Desktop/maios && mkdir -p frontend
```

**Step 2: Create package.json with all dependencies**

```json
{
  "name": "maios-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@react-three/fiber": "^8.17.0",
    "@react-three/drei": "^9.117.0",
    "three": "^0.170.0",
    "@tanstack/react-query": "^5.62.0",
    "zustand": "^5.0.0",
    "framer-motion": "^11.12.0",
    "react-hook-form": "^7.54.0",
    "zod": "^3.24.0",
    "@hookform/resolvers": "^3.9.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.460.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@types/three": "^0.170.0",
    "tailwindcss": "^4.0.0",
    "postcss": "^8.4.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0"
  }
}
```

**Step 3: Install dependencies**

Run: `cd /home/vernox/Desktop/maios/frontend && npm install`
Expected: Dependencies installed successfully

**Step 4: Create TypeScript configuration**

Create `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Step 5: Create Next.js configuration**

Create `frontend/next.config.ts`:
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
```

**Step 6: Create Tailwind CSS configuration**

Create `frontend/tailwind.config.ts`:
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          1: "var(--surface-1)",
          2: "var(--surface-2)",
          3: "var(--surface-3)",
        },
        brand: {
          primary: "var(--brand-primary)",
          secondary: "var(--brand-secondary)",
        },
        line: {
          1: "var(--line-1)",
          2: "var(--line-2)",
        },
        fg: "var(--fg)",
        muted: "var(--muted)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px var(--brand-primary), 0 0 10px var(--brand-primary)" },
          "100%": { boxShadow: "0 0 10px var(--brand-primary), 0 0 20px var(--brand-primary)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

**Step 7: Create global CSS with brand tokens**

Create `frontend/app/globals.css`:
```css
@import "tailwindcss";

:root {
  --fg: #f0f0f0;
  --muted: #888888;
  --surface-1: #0d0d0d;
  --surface-2: #1a1a1a;
  --surface-3: #2a2a2a;
  --line-1: #333333;
  --line-2: #444444;
  --brand-primary: #00e5ff;
  --brand-secondary: #7c3aed;
  --brand-tertiary: #00ff88;
  --glow-primary: rgba(0, 229, 255, 0.3);
}

* {
  box-sizing: border-box;
}

body {
  background: var(--surface-1);
  color: var(--fg);
  font-family: system-ui, -apple-system, sans-serif;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface-1);
}

::-webkit-scrollbar-thumb {
  background: var(--line-1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--line-2);
}
```

**Step 8: Create root layout**

Create `frontend/app/layout.tsx`:
```tsx
import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "MAIOS - Metamorphic AI Orchestration",
  description: "Multi-Agent AI Orchestration System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**Step 9: Create providers component**

Create `frontend/app/providers.tsx`:
```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

**Step 10: Create landing page**

Create `frontend/app/page.tsx`:
```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-4" style={{ color: "var(--brand-primary)" }}>
          MAIOS
        </h1>
        <p className="text-xl text-muted mb-8">
          Metamorphic AI Orchestration System
        </p>
        <Link
          href="/dashboard"
          className="px-6 py-3 rounded-lg font-medium transition-all duration-200"
          style={{
            background: "var(--brand-primary)",
            color: "var(--surface-1)",
          }}
        >
          Enter Dashboard
        </Link>
      </div>
    </main>
  );
}
```

**Step 11: Commit project initialization**

```bash
git add frontend/
git commit -m "feat(frontend): initialize Next.js 15 project with TypeScript and Tailwind"
```

---

## Task 2: Core Layout Components

**Files:**
- Create: `frontend/app/(dashboard)/layout.tsx`
- Create: `frontend/components/layout/Sidebar.tsx`
- Create: `frontend/components/layout/Header.tsx`
- Create: `frontend/lib/utils.ts`

**Step 1: Create utility functions**

Create `frontend/lib/utils.ts`:
```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Step 2: Create Sidebar component**

Create `frontend/components/layout/Sidebar.tsx`:
```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  Brain,
  Settings,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/projects", label: "Projects", icon: FolderKanban },
  { href: "/dashboard/agents", label: "Agents", icon: Users },
  { href: "/dashboard/memory", label: "Memory", icon: Brain },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="w-64 h-screen flex flex-col"
      style={{
        background: "var(--surface-1)",
        borderRight: "1px solid var(--line-1)",
      }}
    >
      <div className="p-4 border-b" style={{ borderColor: "var(--line-1)" }}>
        <h1
          className="text-xl font-bold"
          style={{ color: "var(--brand-primary)" }}
        >
          MAIOS
        </h1>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200",
                    isActive
                      ? "bg-surface-2 text-[var(--brand-primary)]"
                      : "text-muted hover:text-fg hover:bg-surface-2"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
```

**Step 3: Create Header component**

Create `frontend/components/layout/Header.tsx`:
```tsx
"use client";

import { Bell, Search, User } from "lucide-react";

export function Header() {
  return (
    <header
      className="h-16 flex items-center justify-between px-6"
      style={{
        background: "var(--surface-1)",
        borderBottom: "1px solid var(--line-1)",
      }}
    >
      <div className="flex items-center gap-4">
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{ background: "var(--surface-2)" }}
        >
          <Search className="w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent border-none outline-none text-sm w-48"
          />
          <kbd
            className="px-2 py-0.5 text-xs rounded"
            style={{ background: "var(--surface-3)" }}
          >
            ⌘K
          </kbd>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button
          className="p-2 rounded-lg hover:bg-surface-2 transition-colors relative"
        >
          <Bell className="w-5 h-5 text-muted" />
          <span
            className="absolute top-1 right-1 w-2 h-2 rounded-full"
            style={{ background: "var(--brand-primary)" }}
          />
        </button>
        <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface-2 transition-colors">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: "var(--brand-secondary)" }}
          >
            <User className="w-4 h-4" />
          </div>
        </button>
      </div>
    </header>
  );
}
```

**Step 4: Create dashboard layout**

Create `frontend/app/(dashboard)/layout.tsx`:
```tsx
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main
          className="flex-1 overflow-auto p-6"
          style={{ background: "var(--surface-2)" }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
```

**Step 5: Create dashboard page**

Create `frontend/app/(dashboard)/page.tsx`:
```tsx
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Active Agents" value="12" trend="+2" />
        <StatCard title="Running Tasks" value="8" trend="+3" />
        <StatCard title="Completed Today" value="24" trend="+15" />
        <StatCard title="Avg Response" value="1.2s" trend="-0.3s" />
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  trend,
}: {
  title: string;
  value: string;
  trend: string;
}) {
  const isPositive = trend.startsWith("+") || trend.startsWith("-");
  return (
    <div
      className="p-4 rounded-lg"
      style={{
        background: "var(--surface-1)",
        border: "1px solid var(--line-1)",
      }}
    >
      <p className="text-sm text-muted">{title}</p>
      <div className="flex items-end justify-between mt-2">
        <span className="text-2xl font-bold">{value}</span>
        <span
          className="text-sm"
          style={{
            color: trend.startsWith("+")
              ? "var(--brand-tertiary)"
              : trend.startsWith("-")
              ? "var(--brand-secondary)"
              : "var(--muted)",
          }}
        >
          {trend}
        </span>
      </div>
    </div>
  );
}
```

**Step 6: Commit layout components**

```bash
git add frontend/
git commit -m "feat(frontend): add dashboard layout with sidebar and header"
```

---

## Task 3: API Client and WebSocket

**Files:**
- Create: `frontend/lib/api-client.ts`
- Create: `frontend/lib/websocket.ts`
- Create: `frontend/hooks/useWebSocket.ts`
- Create: `frontend/types/api.ts`

**Step 1: Create API types**

Create `frontend/types/api.ts`:
```typescript
export interface Agent {
  id: string;
  name: string;
  role: string;
  status: "idle" | "busy" | "error" | "offline";
  performance_score: number;
  tasks_completed: number;
  tasks_failed: number;
  current_task_id: string | null;
  last_heartbeat: string | null;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: "pending" | "assigned" | "in_progress" | "completed" | "failed" | "blocked";
  priority: "low" | "medium" | "high" | "urgent";
  project_id: string;
  assigned_agent_id: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: "active" | "paused" | "completed" | "archived";
  created_at: string;
  updated_at: string;
}

export interface MemoryEntry {
  id: string;
  key: string;
  value: string;
  memory_type: string;
  tags: string[];
  created_at: string;
  last_accessed_at: string | null;
}

export interface WebSocketMessage {
  type: string;
  payload: unknown;
}
```

**Step 2: Create API client**

Create `frontend/lib/api-client.ts`:
```typescript
import type { Agent, Task, Project, MemoryEntry } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

class ApiClient {
  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    return this.fetch<Agent[]>("/agents");
  }

  async getAgent(id: string): Promise<Agent> {
    return this.fetch<Agent>(`/agents/${id}`);
  }

  async createAgent(data: Partial<Agent>): Promise<Agent> {
    return this.fetch<Agent>("/agents", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Tasks
  async getTasks(params?: { project_id?: string; status?: string }): Promise<Task[]> {
    const searchParams = new URLSearchParams();
    if (params?.project_id) searchParams.set("project_id", params.project_id);
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return this.fetch<Task[]>(`/tasks${query ? `?${query}` : ""}`);
  }

  async getTask(id: string): Promise<Task> {
    return this.fetch<Task>(`/tasks/${id}`);
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    return this.fetch<Project[]>("/projects");
  }

  async getProject(id: string): Promise<Project> {
    return this.fetch<Project>(`/projects/${id}`);
  }

  async createProject(data: Partial<Project>): Promise<Project> {
    return this.fetch<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Memory
  async searchMemory(query: string): Promise<MemoryEntry[]> {
    return this.fetch<MemoryEntry[]>("/memory/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  }
}

export const apiClient = new ApiClient();
```

**Step 3: Create WebSocket client**

Create `frontend/lib/websocket.ts`:
```typescript
import type { WebSocketMessage } from "@/types/api";

type MessageHandler = (message: WebSocketMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(url: string = "ws://localhost:8000/ws"): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      this.attemptReconnect(url);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    return () => {
      this.handlers.get(eventType)?.delete(handler);
    };
  }

  send(message: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.handlers.get(message.type);
    if (handlers) {
      handlers.forEach((handler) => handler(message));
    }

    // Also call wildcard handlers
    const wildcardHandlers = this.handlers.get("*");
    if (wildcardHandlers) {
      wildcardHandlers.forEach((handler) => handler(message));
    }
  }

  private attemptReconnect(url: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      console.log(`Reconnecting (attempt ${this.reconnectAttempts})...`);
      this.connect(url);
    }, delay);
  }
}

export const wsClient = new WebSocketClient();
```

**Step 4: Create useWebSocket hook**

Create `frontend/hooks/useWebSocket.ts`:
```tsx
"use client";

import { useEffect, useRef } from "react";
import { wsClient } from "@/lib/websocket";
import type { WebSocketMessage } from "@/types/api";

export function useWebSocket(
  eventType: string,
  handler: (message: WebSocketMessage) => void
) {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.subscribe(eventType, (message) => {
      handlerRef.current(message);
    });

    return unsubscribe;
  }, [eventType]);
}

export function useWebSocketConnection() {
  useEffect(() => {
    wsClient.connect();
    return () => wsClient.disconnect();
  }, []);
}
```

**Step 5: Commit API and WebSocket**

```bash
git add frontend/
git commit -m "feat(frontend): add API client and WebSocket connection"
```

---

## Task 4: State Management

**Files:**
- Create: `frontend/stores/useUIStore.ts`
- Create: `frontend/stores/useAgentStore.ts`
- Create: `frontend/hooks/useAgents.ts`
- Create: `frontend/hooks/useTasks.ts`

**Step 1: Create UI store**

Create `frontend/stores/useUIStore.ts`:
```typescript
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
```

**Step 2: Create agent store**

Create `frontend/stores/useAgentStore.ts`:
```typescript
import { create } from "zustand";
import type { Agent } from "@/types/api";

interface AgentStore {
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  addAgent: (agent: Agent) => void;
  removeAgent: (id: string) => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, ...updates } : agent
      ),
    })),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  removeAgent: (id) =>
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id),
    })),
}));
```

**Step 3: Create useAgents hook**

Create `frontend/hooks/useAgents.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAgentStore } from "@/stores/useAgentStore";
import type { Agent } from "@/types/api";

export function useAgents() {
  const queryClient = useQueryClient();
  const setAgents = useAgentStore((state) => state.setAgents);

  const query = useQuery({
    queryKey: ["agents"],
    queryFn: async () => {
      const agents = await apiClient.getAgents();
      setAgents(agents);
      return agents;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<Agent>) => apiClient.createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  return {
    agents: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    createAgent: createMutation.mutate,
    isCreating: createMutation.isPending,
  };
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: ["agent", id],
    queryFn: () => apiClient.getAgent(id),
    enabled: !!id,
  });
}
```

**Step 4: Create useTasks hook**

Create `frontend/hooks/useTasks.ts`:
```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function useTasks(params?: { project_id?: string; status?: string }) {
  return useQuery({
    queryKey: ["tasks", params],
    queryFn: () => apiClient.getTasks(params),
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: ["task", id],
    queryFn: () => apiClient.getTask(id),
    enabled: !!id,
  });
}
```

**Step 5: Commit state management**

```bash
git add frontend/
git commit -m "feat(frontend): add Zustand stores and React Query hooks"
```

---

## Task 5: Agent Components

**Files:**
- Create: `frontend/components/agents/AgentCard.tsx`
- Create: `frontend/components/agents/AgentStatusOrb.tsx`
- Create: `frontend/app/(dashboard)/agents/page.tsx`
- Create: `frontend/app/(dashboard)/agents/[id]/page.tsx`

**Step 1: Create AgentStatusOrb component**

Create `frontend/components/agents/AgentStatusOrb.tsx`:
```tsx
"use client";

import { cn } from "@/lib/utils";

interface AgentStatusOrbProps {
  status: "idle" | "busy" | "error" | "offline";
  size?: "sm" | "md" | "lg";
}

const statusColors = {
  idle: "var(--brand-tertiary)",
  busy: "var(--brand-primary)",
  error: "#ef4444",
  offline: "var(--muted)",
};

const sizeClasses = {
  sm: "w-2 h-2",
  md: "w-3 h-3",
  lg: "w-4 h-4",
};

export function AgentStatusOrb({ status, size = "md" }: AgentStatusOrbProps) {
  const isAnimated = status === "busy";

  return (
    <div
      className={cn("rounded-full relative", sizeClasses[size])}
      style={{
        background: statusColors[status],
        boxShadow: isAnimated
          ? `0 0 10px ${statusColors[status]}, 0 0 20px ${statusColors[status]}`
          : `0 0 5px ${statusColors[status]}`,
        animation: isAnimated ? "pulse 1.5s ease-in-out infinite" : "none",
      }}
    />
  );
}
```

**Step 2: Create AgentCard component**

Create `frontend/components/agents/AgentCard.tsx`:
```tsx
"use client";

import Link from "next/link";
import { AgentStatusOrb } from "./AgentStatusOrb";
import type { Agent } from "@/types/api";

interface AgentCardProps {
  agent: Agent;
}

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <Link href={`/dashboard/agents/${agent.id}`}>
      <div
        className="p-4 rounded-lg transition-all duration-200 hover:scale-[1.02] cursor-pointer"
        style={{
          background: "var(--surface-1)",
          border: "1px solid var(--line-1)",
        }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <AgentStatusOrb status={agent.status} size="lg" />
            <div>
              <h3 className="font-medium">{agent.name}</h3>
              <p className="text-sm text-muted">{agent.role}</p>
            </div>
          </div>
          <div
            className="px-2 py-1 rounded text-xs"
            style={{ background: "var(--surface-2)" }}
          >
            Score: {agent.performance_score.toFixed(1)}
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span>Completed: {agent.tasks_completed}</span>
          <span>Failed: {agent.tasks_failed}</span>
        </div>
        {agent.current_task_id && (
          <div className="mt-3 text-sm">
            <span className="text-muted">Current task: </span>
            <span style={{ color: "var(--brand-primary)" }}>
              {agent.current_task_id.slice(0, 8)}...
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}
```

**Step 3: Create agents list page**

Create `frontend/app/(dashboard)/agents/page.tsx`:
```tsx
"use client";

import { useAgents } from "@/hooks/useAgents";
import { AgentCard } from "@/components/agents/AgentCard";

export default function AgentsPage() {
  const { agents, isLoading, error } = useAgents();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div
          className="animate-spin rounded-full h-8 w-8"
          style={{ border: "2px solid var(--brand-primary)" }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 py-8">
        Failed to load agents. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Agents</h1>
        <button
          className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{
            background: "var(--brand-primary)",
            color: "var(--surface-1)",
          }}
        >
          Create Agent
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
      {agents.length === 0 && (
        <div className="text-center text-muted py-12">
          No agents found. Create your first agent to get started.
        </div>
      )}
    </div>
  );
}
```

**Step 4: Create agent detail page**

Create `frontend/app/(dashboard)/agents/[id]/page.tsx`:
```tsx
"use client";

import { useParams } from "next/navigation";
import { useAgent } from "@/hooks/useAgents";
import { AgentStatusOrb } from "@/components/agents/AgentStatusOrb";

export default function AgentDetailPage() {
  const params = useParams();
  const { data: agent, isLoading, error } = useAgent(params.id as string);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div
          className="animate-spin rounded-full h-8 w-8"
          style={{ border: "2px solid var(--brand-primary)" }}
        />
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="text-center text-red-500 py-8">
        Agent not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <AgentStatusOrb status={agent.status} size="lg" />
        <div>
          <h1 className="text-2xl font-bold">{agent.name}</h1>
          <p className="text-muted">{agent.role}</p>
        </div>
      </div>

      <div
        className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-lg"
        style={{ background: "var(--surface-1)", border: "1px solid var(--line-1)" }}
      >
        <div>
          <p className="text-sm text-muted">Performance Score</p>
          <p className="text-xl font-bold" style={{ color: "var(--brand-primary)" }}>
            {agent.performance_score.toFixed(1)}
          </p>
        </div>
        <div>
          <p className="text-sm text-muted">Tasks Completed</p>
          <p className="text-xl font-bold">{agent.tasks_completed}</p>
        </div>
        <div>
          <p className="text-sm text-muted">Tasks Failed</p>
          <p className="text-xl font-bold">{agent.tasks_failed}</p>
        </div>
      </div>

      {agent.last_heartbeat && (
        <div
          className="p-4 rounded-lg"
          style={{ background: "var(--surface-1)", border: "1px solid var(--line-1)" }}
        >
          <p className="text-sm text-muted">Last Heartbeat</p>
          <p>{new Date(agent.last_heartbeat).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}
```

**Step 5: Commit agent components**

```bash
git add frontend/
git commit -m "feat(frontend): add agent components and pages"
```

---

## Task 6: Task Components

**Files:**
- Create: `frontend/components/tasks/TaskCard.tsx`
- Create: `frontend/components/tasks/TaskBoard.tsx`
- Create: `frontend/app/(dashboard)/projects/page.tsx`

**Step 1: Create TaskCard component**

Create `frontend/components/tasks/TaskCard.tsx`:
```tsx
"use client";

import type { Task } from "@/types/api";
import { cn } from "@/lib/utils";

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
}

const priorityColors = {
  low: "var(--brand-tertiary)",
  medium: "var(--brand-primary)",
  high: "#f59e0b",
  urgent: "#ef4444",
};

const statusStyles = {
  pending: { bg: "var(--surface-2)", text: "Pending" },
  assigned: { bg: "var(--surface-3)", text: "Assigned" },
  in_progress: { bg: "var(--brand-primary)", text: "In Progress" },
  completed: { bg: "var(--brand-tertiary)", text: "Completed" },
  failed: { bg: "#ef4444", text: "Failed" },
  blocked: { bg: "#f59e0b", text: "Blocked" },
};

export function TaskCard({ task, onClick }: TaskCardProps) {
  const statusStyle = statusStyles[task.status];

  return (
    <div
      onClick={onClick}
      className="p-3 rounded-lg cursor-pointer transition-all duration-200 hover:scale-[1.02]"
      style={{
        background: "var(--surface-1)",
        border: "1px solid var(--line-1)",
        borderLeft: `3px solid ${priorityColors[task.priority]}`,
      }}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-sm">{task.title}</h4>
        <span
          className="text-xs px-2 py-0.5 rounded"
          style={{
            background: statusStyle.bg,
            color: task.status === "in_progress" ? "var(--surface-1)" : "var(--fg)",
          }}
        >
          {statusStyle.text}
        </span>
      </div>
      {task.description && (
        <p className="text-xs text-muted line-clamp-2 mb-2">{task.description}</p>
      )}
      <div className="flex items-center justify-between text-xs text-muted">
        <span>{task.priority} priority</span>
        <span>{new Date(task.created_at).toLocaleDateString()}</span>
      </div>
    </div>
  );
}
```

**Step 2: Create TaskBoard component**

Create `frontend/components/tasks/TaskBoard.tsx`:
```tsx
"use client";

import type { Task } from "@/types/api";
import { TaskCard } from "./TaskCard";

interface TaskBoardProps {
  tasks: Task[];
}

const columns: { status: Task["status"][]; title: string }[] = [
  { status: ["pending"], title: "Backlog" },
  { status: ["assigned", "in_progress"], title: "In Progress" },
  { status: ["blocked"], title: "Blocked" },
  { status: ["completed"], title: "Done" },
];

export function TaskBoard({ tasks }: TaskBoardProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {columns.map((column) => {
        const columnTasks = tasks.filter((t) => column.status.includes(t.status));
        return (
          <div key={column.title} className="space-y-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-sm">{column.title}</h3>
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{ background: "var(--surface-2)" }}
              >
                {columnTasks.length}
              </span>
            </div>
            <div className="space-y-2">
              {columnTasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

**Step 3: Create projects list page**

Create `frontend/app/(dashboard)/projects/page.tsx`:
```tsx
"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useTasks } from "@/hooks/useTasks";
import { TaskBoard } from "@/components/tasks/TaskBoard";

export default function ProjectsPage() {
  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => apiClient.getProjects(),
  });

  const { data: tasks, isLoading: tasksLoading } = useTasks();

  if (projectsLoading || tasksLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div
          className="animate-spin rounded-full h-8 w-8"
          style={{ border: "2px solid var(--brand-primary)" }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{
            background: "var(--brand-primary)",
            color: "var(--surface-1)",
          }}
        >
          New Project
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {projects?.map((project) => (
          <Link key={project.id} href={`/dashboard/projects/${project.id}`}>
            <div
              className="p-4 rounded-lg transition-all duration-200 hover:scale-[1.02] cursor-pointer"
              style={{
                background: "var(--surface-1)",
                border: "1px solid var(--line-1)",
              }}
            >
              <h3 className="font-medium">{project.name}</h3>
              {project.description && (
                <p className="text-sm text-muted mt-1 line-clamp-2">
                  {project.description}
                </p>
              )}
              <div className="flex items-center gap-2 mt-3">
                <span
                  className="text-xs px-2 py-0.5 rounded"
                  style={{ background: "var(--surface-2)" }}
                >
                  {project.status}
                </span>
                <span className="text-xs text-muted">
                  {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {tasks && tasks.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">All Tasks</h2>
          <TaskBoard tasks={tasks} />
        </div>
      )}
    </div>
  );
}
```

**Step 4: Commit task components**

```bash
git add frontend/
git commit -m "feat(frontend): add task components and project pages"
```

---

## Task 7: 3D Visualization

**Files:**
- Create: `frontend/components/visualization/NeuralGraph.tsx`
- Create: `frontend/components/visualization/AgentNode.tsx`
- Create: `frontend/app/(dashboard)/neural/page.tsx`

**Step 1: Create AgentNode component**

Create `frontend/components/visualization/AgentNode.tsx`:
```tsx
"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import type { Mesh, Vector3 } from "three";

interface AgentNodeProps {
  position: [number, number, number];
  name: string;
  role: string;
  status: "idle" | "busy" | "error" | "offline";
  onClick?: () => void;
}

const statusColors = {
  idle: "#00ff88",
  busy: "#00e5ff",
  error: "#ef4444",
  offline: "#888888",
};

export function AgentNode({
  position,
  name,
  role,
  status,
  onClick,
}: AgentNodeProps) {
  const meshRef = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const color = statusColors[status];
  const isAnimated = status === "busy";

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing effect for busy agents
      if (isAnimated) {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1;
        meshRef.current.scale.setScalar(scale);
      }
      // Hover glow effect
      if (hovered) {
        meshRef.current.scale.setScalar(1.2);
      }
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 0.8 : 0.3}
        />
      </mesh>
      {/* Outer glow ring */}
      <mesh>
        <ringGeometry args={[0.6, 0.65, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.3} />
      </mesh>
      {/* Name label */}
      <Text
        position={[0, 0.8, 0]}
        fontSize={0.2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
      >
        {name}
      </Text>
      {/* Role label */}
      <Text
        position={[0, 0.55, 0]}
        fontSize={0.12}
        color="#888888"
        anchorX="center"
        anchorY="middle"
      >
        {role}
      </Text>
    </group>
  );
}
```

**Step 2: Create NeuralGraph component**

Create `frontend/components/visualization/NeuralGraph.tsx``:
```tsx
"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { AgentNode } from "./AgentNode";
import type { Agent } from "@/types/api";

interface NeuralGraphProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
}

// Simple force-directed layout for positioning nodes
function calculatePositions(agents: Agent[]): Map<string, [number, number, number]> {
  const positions = new Map<string, [number, number, number]>();
  const count = agents.length;

  agents.forEach((agent, i) => {
    // Distribute in a sphere pattern
    const phi = Math.acos(-1 + (2 * i) / count);
    const theta = Math.sqrt(count * Math.PI) * phi;
    const radius = 3;

    positions.set(agent.id, [
      radius * Math.cos(theta) * Math.sin(phi),
      radius * Math.sin(theta) * Math.sin(phi),
      radius * Math.cos(phi),
    ]);
  });

  return positions;
}

export function NeuralGraph({ agents, onAgentClick }: NeuralGraphProps) {
  const positions = calculatePositions(agents);

  return (
    <Canvas
      camera={{ position: [0, 0, 8], fov: 60 }}
      style={{ background: "var(--surface-1)" }}
    >
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <Environment preset="night" />

      {agents.map((agent) => (
        <AgentNode
          key={agent.id}
          position={positions.get(agent.id) || [0, 0, 0]}
          name={agent.name}
          role={agent.role}
          status={agent.status}
          onClick={() => onAgentClick?.(agent)}
        />
      ))}

      {/* Connection lines between agents */}
      {agents.length > 1 &&
        agents.slice(0, -1).map((agent, i) => {
          const nextAgent = agents[i + 1];
          const start = positions.get(agent.id);
          const end = positions.get(nextAgent.id);
          if (!start || !end) return null;

          return (
            <line key={`line-${agent.id}-${nextAgent.id}`}>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={2}
                  array={new Float32Array([...start, ...end])}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial color="#333333" transparent opacity={0.3} />
            </line>
          );
        })}

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        autoRotate={false}
      />
    </Canvas>
  );
}
```

**Step 3: Create neural view page**

Create `frontend/app/(dashboard)/neural/page.tsx`:
```tsx
"use client";

import { useRouter } from "next/navigation";
import { NeuralGraph } from "@/components/visualization/NeuralGraph";
import { useAgents } from "@/hooks/useAgents";
import { useUIStore } from "@/stores/useUIStore";
import type { Agent } from "@/types/api";

export default function NeuralPage() {
  const router = useRouter();
  const { agents, isLoading } = useAgents();
  const setSelectedAgentId = useUIStore((state) => state.setSelectedAgentId);

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgentId(agent.id);
    router.push(`/dashboard/agents/${agent.id}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div
          className="animate-spin rounded-full h-8 w-8"
          style={{ border: "2px solid var(--brand-primary)" }}
        />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)] rounded-lg overflow-hidden" style={{ border: "1px solid var(--line-1)" }}>
      <NeuralGraph agents={agents} onAgentClick={handleAgentClick} />
    </div>
  );
}
```

**Step 4: Update sidebar to include Neural view**

Modify `frontend/components/layout/Sidebar.tsx` to add Neural link:
```tsx
// Add to navItems array:
{ href: "/dashboard/neural", label: "Neural View", icon: Network },
```

**Step 5: Commit 3D visualization**

```bash
git add frontend/
git commit -m "feat(frontend): add 3D neural graph visualization"
```

---

## Task 8: Final Integration

**Files:**
- Create: `frontend/next-env.d.ts`
- Update: `frontend/components/layout/Sidebar.tsx`
- Update: `frontend/package.json`

**Step 1: Create next-env.d.ts**

Create `frontend/next-env.d.ts`:
```typescript
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
```

**Step 2: Add Network icon to Sidebar**

Update `frontend/components/layout/Sidebar.tsx` to import Network icon:
```tsx
import { Network } from "lucide-react";
```

And add Neural view to navItems:
```tsx
{ href: "/dashboard/neural", label: "Neural View", icon: Network },
```

**Step 3: Run build to verify everything works**

Run: `cd /home/vernox/Desktop/maios/frontend && npm run build`
Expected: Build succeeds without errors

**Step 4: Final commit**

```bash
git add frontend/
git commit -m "feat(frontend): complete MAIOS frontend with 3D visualization"
```
