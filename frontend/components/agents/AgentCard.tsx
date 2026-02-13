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
