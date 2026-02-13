"use client";

import type { Task } from "@/types/api";

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
