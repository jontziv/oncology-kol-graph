import { useQuery } from "@tanstack/react-query";
import type { DiseaseBurdenRecord } from "@/types";
import { API_BASE } from "./config";

async function fetchDiseaseBurden(): Promise<DiseaseBurdenRecord[]> {
  const res = await fetch(`${API_BASE}/api/disease-burden`);
  if (!res.ok) throw new Error("Failed to fetch disease burden data");
  return res.json();
}

export function useDiseaseBurden() {
  return useQuery({
    queryKey: ["disease-burden"],
    queryFn: fetchDiseaseBurden,
    staleTime: 30 * 60 * 1000,
  });
}
