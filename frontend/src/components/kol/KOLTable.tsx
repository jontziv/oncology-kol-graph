import { useState } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";
import type { KOLSummary } from "@/types";
import { cn, scoreBg } from "@/lib/utils";
import { ConflictBadge } from "@/components/shared/ConflictBadge";

interface KOLTableProps {
  kols: KOLSummary[];
  selectedNpi: string | null;
  onSelect: (npi: string) => void;
  onSortChange: (field: string) => void;
  sortBy: string;
  className?: string;
}

type SortDir = "asc" | "desc";

const COLUMNS = [
  { key: "name", label: "Investigator" },
  { key: "kol_score", label: "KOL" },
  { key: "trial_score", label: "Trial" },
  { key: "pub_score", label: "Pub" },
  { key: "payment_total_usd", label: "Payments" },
];

export function KOLTable({
  kols,
  selectedNpi,
  onSelect,
  onSortChange,
  sortBy,
  className,
}: KOLTableProps) {
  const [sortDir] = useState<SortDir>("desc");

  return (
    <div className={cn("overflow-auto", className)}>
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-slate-900 border-b border-slate-700">
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                onClick={() => onSortChange(col.key)}
                className="px-3 py-2 text-left text-xs font-medium text-slate-400 cursor-pointer hover:text-slate-200 whitespace-nowrap select-none"
              >
                <span className="flex items-center gap-1">
                  {col.label}
                  {sortBy === col.key && (
                    sortDir === "desc"
                      ? <ChevronDown className="w-3 h-3" />
                      : <ChevronUp className="w-3 h-3" />
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {kols.map((kol) => (
            <tr
              key={kol.npi}
              onClick={() => onSelect(kol.npi)}
              className={cn(
                "border-b border-slate-800 cursor-pointer transition-colors",
                selectedNpi === kol.npi
                  ? "bg-sky-500/10 border-sky-500/20"
                  : "hover:bg-slate-800/60"
              )}
            >
              <td className="px-3 py-2.5">
                <div className="font-medium text-slate-200 text-xs leading-tight truncate max-w-[140px]">
                  {kol.name}
                </div>
                <div className="text-xs text-slate-500 truncate max-w-[140px]">
                  {kol.institution_name ?? kol.state}
                </div>
              </td>
              <td className="px-3 py-2.5">
                <span className={cn("text-xs font-semibold px-1.5 py-0.5 rounded border", scoreBg(kol.kol_score))}>
                  {kol.kol_score.toFixed(0)}
                </span>
              </td>
              <td className="px-3 py-2.5 text-xs text-slate-400">{kol.trial_score.toFixed(0)}</td>
              <td className="px-3 py-2.5 text-xs text-slate-400">{kol.pub_score.toFixed(0)}</td>
              <td className="px-3 py-2.5">
                <ConflictBadge
                  totalUsd={kol.payment_total_usd}
                  companyCount={kol.payment_company_count}
                  showLabel={false}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
