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
