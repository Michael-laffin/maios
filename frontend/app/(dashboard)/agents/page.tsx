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
