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
