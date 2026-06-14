import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { API_BASE } from "./config";
import { useAuth } from "@/contexts/AuthContext";

export interface Engagement {
  id: string;
  npi: string;
  status: "To Engage" | "Engaged" | "Declined";
  notes: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
}

async function fetchEngagement(npi: string, userToken: string): Promise<Engagement | null> {
  const res = await fetch(`${API_BASE}/api/engagements/${npi}`, {
    headers: {
      Authorization: `Bearer ${userToken}`,
      "X-User-ID": npi, // Placeholder — frontend will send actual user ID
    },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch engagement");
  return res.json();
}

async function saveEngagement(
  npi: string,
  status: string,
  notes: string,
  assigned_to: string,
  userToken: string
): Promise<Engagement> {
  const res = await fetch(`${API_BASE}/api/engagements`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userToken}`,
      "X-User-ID": npi,
    },
    body: JSON.stringify({ npi, status, notes, assigned_to }),
  });
  if (!res.ok) throw new Error("Failed to save engagement");
  return res.json();
}

export function useEngagement(npi: string | null) {
  const { session } = useAuth();

  return useQuery({
    queryKey: ["engagement", npi],
    queryFn: () => fetchEngagement(npi!, session?.access_token || ""),
    enabled: !!npi && !!session,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSaveEngagement() {
  const queryClient = useQueryClient();
  const { session } = useAuth();

  return useMutation({
    mutationFn: ({ npi, status, notes, assigned_to }: Omit<Engagement, "id" | "created_at" | "updated_at">) =>
      saveEngagement(npi, status, notes, assigned_to, session?.access_token || ""),
    onSuccess: (data) => {
      queryClient.setQueryData(["engagement", data.npi], data);
    },
  });
}
