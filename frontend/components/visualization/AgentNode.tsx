"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import type { Mesh } from "three";

interface AgentNodeProps {
  position: [number, number, number];
  name: string;
  role: string;
  status: "idle" | "busy" | "error" | "offline";
  onClick?: () => void;
}

const statusColors = {
  idle: "#00ff88",
  busy: "#00e5ff",
  error: "#ef4444",
  offline: "#888888",
};

export function AgentNode({
  position,
  name,
  role,
  status,
  onClick,
}: AgentNodeProps) {
  const meshRef = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const color = statusColors[status];
  const isAnimated = status === "busy";

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing effect for busy agents
      if (isAnimated) {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1;
        meshRef.current.scale.setScalar(scale);
      }
      // Hover glow effect
      if (hovered) {
        meshRef.current.scale.setScalar(1.2);
      }
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 0.8 : 0.3}
        />
      </mesh>
      {/* Name label */}
      <Text
        position={[0, 0.8, 0]}
        fontSize={0.2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
      >
        {name}
      </Text>
      {/* Role label */}
      <Text
        position={[0, 0.55, 0]}
        fontSize={0.12}
        color="#888888"
        anchorX="center"
        anchorY="middle"
      >
        {role}
      </Text>
    </group>
  );
}
