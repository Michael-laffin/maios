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
