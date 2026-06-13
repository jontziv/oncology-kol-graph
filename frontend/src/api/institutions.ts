import { useQuery } from "@tanstack/react-query";
import type { InstitutionSummary } from "@/types";

async function fetchInstitutions(sortBy = "trial_count", state = ""): Promise<InstitutionSummary[]> {
  const params = new URLSearchParams({ sort_by: sortBy, ...(state && { state }) });
  const res = await fetch(`/api/institutions?${params}`);
  if (!res.ok) throw new Error("Failed to fetch institutions");
  return res.json();
}

export function useInstitutions(sortBy?: string, state?: string) {
  return useQuery({
    queryKey: ["institutions", sortBy, state],
    queryFn: () => fetchInstitutions(sortBy, state),
    staleTime: 5 * 60 * 1000,
  });
}
