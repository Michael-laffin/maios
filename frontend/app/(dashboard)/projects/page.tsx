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
