import { useState } from "react";
import { useInstitutions } from "@/api/institutions";
import { useDiseaseBurden } from "@/api/diseaseBurden";
import { DiseaseBurdenMap } from "@/components/map/DiseaseBurdenMap";
import { LoadingOverlay } from "@/components/shared/LoadingSpinner";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

type SortField = "trial_count" | "kol_count" | "disease_burden_rate" | "name";

const COLUMNS: { key: SortField; label: string }[] = [
  { key: "name", label: "Institution" },
  { key: "kol_count", label: "KOLs" },
  { key: "trial_count", label: "Trials" },
  { key: "disease_burden_rate", label: "NSCLC Rate" },
];

export function InstitutionsPage() {
  const [sortBy, setSortBy] = useState<SortField>("trial_count");
  const [stateFilter, setStateFilter] = useState("");

  const { data: institutions, isLoading } = useInstitutions(sortBy, stateFilter);
  const { data: burden } = useDiseaseBurden();

  return (
    <div className="flex flex-col h-[calc(100vh-48px)]">
      {/* Map */}
      <div className="px-6 py-4 border-b border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-200">
            NSCLC Disease Burden (SEER, 2021)
          </h2>
          <span className="text-xs text-slate-500">Incidence per 100,000 · Amber dots = trial sites</span>
        </div>
        {burden ? (
          <DiseaseBurdenMap
            burdenData={burden}
            institutions={institutions ?? []}
            onStateClick={setStateFilter}
          />
        ) : (
          <div className="h-64 flex items-center justify-center text-slate-600 text-sm">
            Loading map data...
          </div>
        )}
        {stateFilter && (
          <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
            <span>Filtered to: <strong className="text-slate-200">{stateFilter}</strong></span>
            <button onClick={() => setStateFilter("")} className="text-sky-400 hover:text-sky-300 underline">
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <LoadingOverlay label="Loading institutions..." />
        ) : (
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-slate-950 border-b border-slate-700">
              <tr>
                {COLUMNS.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => setSortBy(col.key)}
                    className="px-3 py-2 text-left text-xs font-medium text-slate-400 cursor-pointer hover:text-slate-200 whitespace-nowrap select-none"
                  >
                    <span className="flex items-center gap-1">
                      {col.label}
                      {sortBy === col.key && <ChevronDown className="w-3 h-3" />}
                    </span>
                  </th>
                ))}
                <th className="px-3 py-2 text-left text-xs text-slate-400">Type</th>
                <th className="px-3 py-2 text-left text-xs text-slate-400">Location</th>
              </tr>
            </thead>
            <tbody>
              {(institutions ?? []).map((inst) => (
                <tr key={inst.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="px-3 py-2.5">
                    <span className="font-medium text-slate-200 text-xs">{inst.name}</span>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{inst.kol_count}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{inst.trial_count}</td>
                  <td className="px-3 py-2.5 text-xs">
                    {inst.disease_burden_rate != null ? (
                      <span className={cn(
                        "font-medium",
                        inst.disease_burden_rate >= 70 ? "text-rose-400" :
                        inst.disease_burden_rate >= 55 ? "text-amber-400" : "text-emerald-400"
                      )}>
                        {inst.disease_burden_rate.toFixed(1)}
                      </span>
                    ) : "—"}
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{inst.type ?? "—"}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">
                    {[inst.city, inst.state].filter(Boolean).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
