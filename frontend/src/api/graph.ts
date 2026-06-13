import { useQuery } from "@tanstack/react-query";
import type { GraphData } from "@/types";

const BASE = "/api";

async function fetchGraph(minScore: number, state: string): Promise<GraphData> {
  const params = new URLSearchParams({
    ...(minScore > 0 && { min_score: String(minScore) }),
    ...(state && { state }),
  });
  const res = await fetch(`${BASE}/graph?${params}`);
  if (!res.ok) throw new Error("Failed to fetch graph");
  return res.json();
}

async function fetchKOLNetwork(npi: string): Promise<GraphData> {
  const res = await fetch(`${BASE}/graph/network/${npi}`);
  if (!res.ok) throw new Error("Failed to fetch KOL network");
  return res.json();
}

export function useGraph(minScore: number, state: string) {
  return useQuery({
    queryKey: ["graph", minScore, state],
    queryFn: () => fetchGraph(minScore, state),
    staleTime: 5 * 60 * 1000,
  });
}

export function useKOLNetwork(npi: string | null) {
  return useQuery({
    queryKey: ["kol-network", npi],
    queryFn: () => fetchKOLNetwork(npi!),
    enabled: !!npi,
    staleTime: 5 * 60 * 1000,
  });
}
