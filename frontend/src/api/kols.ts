import { useQuery } from "@tanstack/react-query";
import type { KOLListResponse, KOLDetail, KOLFilters } from "@/types";

const BASE = "/api";

async function fetchKOLs(
  page: number,
  filters: KOLFilters,
  sortBy = "kol_score",
  order: "asc" | "desc" = "desc"
): Promise<KOLListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "20",
    sort_by: sortBy,
    order,
    ...(filters.state && { state: filters.state }),
    ...(filters.minScore > 0 && { min_score: String(filters.minScore) }),
  });
  const res = await fetch(`${BASE}/kols?${params}`);
  if (!res.ok) throw new Error("Failed to fetch KOLs");
  return res.json();
}

async function fetchKOL(npi: string): Promise<KOLDetail> {
  const res = await fetch(`${BASE}/kols/${npi}`);
  if (!res.ok) throw new Error("Failed to fetch KOL detail");
  return res.json();
}

export function useKOLs(page: number, filters: KOLFilters, sortBy?: string) {
  return useQuery({
    queryKey: ["kols", page, filters, sortBy],
    queryFn: () => fetchKOLs(page, filters, sortBy),
    staleTime: 5 * 60 * 1000,
  });
}

export function useKOL(npi: string | null) {
  return useQuery({
    queryKey: ["kol", npi],
    queryFn: () => fetchKOL(npi!),
    enabled: !!npi,
    staleTime: 5 * 60 * 1000,
  });
}
