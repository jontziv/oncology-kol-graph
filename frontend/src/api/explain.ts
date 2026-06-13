import { useQuery } from "@tanstack/react-query";
import type { ExplanationResponse } from "@/types";
import { API_BASE } from "./config";

async function fetchExplanation(npi: string, refresh = false): Promise<ExplanationResponse> {
  const params = refresh ? "?refresh=true" : "";
  const res = await fetch(`${API_BASE}/api/explain/${npi}${params}`);
  if (!res.ok) throw new Error("Failed to generate explanation");
  return res.json();
}

export function useExplanation(npi: string | null) {
  return useQuery({
    queryKey: ["explain", npi],
    queryFn: () => fetchExplanation(npi!),
    enabled: !!npi,
    staleTime: 7 * 24 * 60 * 60 * 1000, // 7 days — matches backend cache
    retry: 1,
  });
}

export async function refreshExplanation(npi: string): Promise<ExplanationResponse> {
  return fetchExplanation(npi, true);
}
