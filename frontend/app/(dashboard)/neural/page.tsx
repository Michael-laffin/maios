"use client";

import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useAgents } from "@/hooks/useAgents";
import { useUIStore } from "@/stores/useUIStore";
import type { Agent } from "@/types/api";

// Dynamically import NeuralGraph to avoid SSR issues with Three.js
const NeuralGraph = dynamic(
  () => import("@/components/visualization/NeuralGraph").then((mod) => mod.NeuralGraph),
  { ssr: false }
);

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
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Neural View</h1>
      <div
        className="h-[calc(100vh-200px)] rounded-lg overflow-hidden"
        style={{ border: "1px solid var(--line-1)" }}
      >
        <NeuralGraph agents={agents} onAgentClick={handleAgentClick} />
      </div>
    </div>
  );
}
