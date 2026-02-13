"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { AgentNode } from "./AgentNode";
import type { Agent } from "@/types/api";

interface NeuralGraphProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
}

// Simple force-directed layout for positioning nodes
function calculatePositions(agents: Agent[]): Map<string, [number, number, number]> {
  const positions = new Map<string, [number, number, number]>();
  const count = agents.length;

  agents.forEach((agent, i) => {
    // Distribute in a sphere pattern
    const phi = Math.acos(-1 + (2 * i) / count);
    const theta = Math.sqrt(count * Math.PI) * phi;
    const radius = 3;

    positions.set(agent.id, [
      radius * Math.cos(theta) * Math.sin(phi),
      radius * Math.sin(theta) * Math.sin(phi),
      radius * Math.cos(phi),
    ]);
  });

  return positions;
}

export function NeuralGraph({ agents, onAgentClick }: NeuralGraphProps) {
  const positions = calculatePositions(agents);

  return (
    <Canvas
      camera={{ position: [0, 0, 8], fov: 60 }}
      style={{ background: "var(--surface-1)" }}
    >
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <Environment preset="night" />

      {agents.map((agent) => (
        <AgentNode
          key={agent.id}
          position={positions.get(agent.id) || [0, 0, 0]}
          name={agent.name}
          role={agent.role}
          status={agent.status}
          onClick={() => onAgentClick?.(agent)}
        />
      ))}

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        autoRotate={false}
      />
    </Canvas>
  );
}
