import { useQuery } from "@tanstack/react-query";
import type { PaymentRecord } from "@/types";

async function fetchAllPayments(
  page: number,
  year?: number,
  company?: string,
  nature?: string
): Promise<PaymentRecord[]> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "50",
    ...(year && { year: String(year) }),
    ...(company && { company }),
    ...(nature && { nature }),
  });
  const res = await fetch(`/api/payments?${params}`);
  if (!res.ok) throw new Error("Failed to fetch payments");
  return res.json();
}

export function useAllPayments(page: number, year?: number, company?: string, nature?: string) {
  return useQuery({
    queryKey: ["payments", page, year, company, nature],
    queryFn: () => fetchAllPayments(page, year, company, nature),
    staleTime: 5 * 60 * 1000,
  });
}
