import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function useTasks(params?: { project_id?: string; status?: string }) {
  return useQuery({
    queryKey: ["tasks", params],
    queryFn: () => apiClient.getTasks(params),
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: ["task", id],
    queryFn: () => apiClient.getTask(id),
    enabled: !!id,
  });
}
