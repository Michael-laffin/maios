import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAgentStore } from "@/stores/useAgentStore";
import type { Agent } from "@/types/api";

export function useAgents() {
  const queryClient = useQueryClient();
  const setAgents = useAgentStore((state) => state.setAgents);

  const query = useQuery({
    queryKey: ["agents"],
    queryFn: async () => {
      const agents = await apiClient.getAgents();
      setAgents(agents);
      return agents;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<Agent>) => apiClient.createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  return {
    agents: query.data ?? [],
    isLoading: query.isLoading,
    error: query.error,
    createAgent: createMutation.mutate,
    isCreating: createMutation.isPending,
  };
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: ["agent", id],
    queryFn: () => apiClient.getAgent(id),
    enabled: !!id,
  });
}
