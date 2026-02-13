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
