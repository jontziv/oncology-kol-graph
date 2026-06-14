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

async function fetchEngagement(npi: string, userToken: string, userId: string): Promise<Engagement | null> {
  const res = await fetch(`${API_BASE}/api/engagements/${npi}`, {
    headers: {
      Authorization: `Bearer ${userToken}`,
      "X-User-ID": userId,
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
  userToken: string,
  userId: string
): Promise<Engagement> {
  const res = await fetch(`${API_BASE}/api/engagements`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userToken}`,
      "X-User-ID": userId,
    },
    body: JSON.stringify({ npi, status, notes, assigned_to }),
  });
  if (!res.ok) throw new Error("Failed to save engagement");
  return res.json();
}

export function useEngagement(npi: string | null) {
  const { session } = useAuth();
  const userId = session?.user?.id;

  return useQuery({
    queryKey: ["engagement", npi, userId],
    queryFn: async () => {
      if (!npi || !session?.access_token || !userId) {
        return null;
      }
      return fetchEngagement(npi, session.access_token, userId);
    },
    enabled: !!npi && !!session && !!userId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSaveEngagement() {
  const queryClient = useQueryClient();
  const { session } = useAuth();
  const userId = session?.user?.id;

  return useMutation({
    mutationFn: async ({ npi, status, notes, assigned_to }: Omit<Engagement, "id" | "created_at" | "updated_at">) => {
      if (!session?.access_token || !userId) {
        throw new Error("Not authenticated");
      }
      return saveEngagement(npi, status, notes, assigned_to, session.access_token, userId);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["engagement", data.npi, userId], data);
    },
  });
}
