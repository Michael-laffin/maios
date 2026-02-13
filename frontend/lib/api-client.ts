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
