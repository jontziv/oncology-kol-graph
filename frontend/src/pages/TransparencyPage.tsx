import { useState } from "react";
import { useAllPayments } from "@/api/payments";
import { LoadingOverlay } from "@/components/shared/LoadingSpinner";
import { formatCurrency } from "@/lib/utils";
import { ShieldAlert, ChevronLeft, ChevronRight } from "lucide-react";

export function TransparencyPage() {
  const [page, setPage] = useState(1);
  const [yearFilter, setYearFilter] = useState<number | undefined>();
  const [companyFilter, setCompanyFilter] = useState("");

  const { data: payments, isLoading } = useAllPayments(page, yearFilter, companyFilter);

  const years = [2022, 2023];

  return (
    <div className="p-6 space-y-4">
      {/* Compliance banner */}
      <div className="flex items-start gap-3 p-4 bg-sky-500/5 border border-sky-500/20 rounded-lg">
        <ShieldAlert className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
        <div className="text-sm text-slate-300 leading-relaxed">
          <strong className="text-sky-400">Open Payments Transparency View.</strong>{" "}
          All payment data sourced from the{" "}
          <a
            href="https://openpaymentsdata.cms.gov"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-400 hover:underline"
          >
            CMS Open Payments database
          </a>{" "}
          (public record). Disclosure of financial relationships does not indicate
          wrongdoing and does not preclude compliant scientific engagement per PhRMA Code guidelines.
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={yearFilter ?? ""}
          onChange={(e) => {
            setYearFilter(e.target.value ? Number(e.target.value) : undefined);
            setPage(1);
          }}
          className="bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-sky-500"
        >
          <option value="">All years</option>
          {years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>

        <input
          type="text"
          placeholder="Filter by company..."
          value={companyFilter}
          onChange={(e) => { setCompanyFilter(e.target.value); setPage(1); }}
          className="bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-sky-500 w-56"
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <LoadingOverlay label="Loading payment records..." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-700">
              <tr>
                {["Company", "Amount", "Nature of Payment", "Year", "Record ID"].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-xs font-medium text-slate-400">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(payments ?? []).map((p) => (
                <tr key={p.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="px-3 py-2.5 text-xs text-slate-200 max-w-xs truncate">
                    {p.company_name ?? "—"}
                  </td>
                  <td className="px-3 py-2.5 text-xs font-medium text-slate-100">
                    {formatCurrency(p.amount_usd)}
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{p.nature_of_payment ?? "—"}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{p.year ?? "—"}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-600 font-mono truncate max-w-[120px]">
                    {p.record_id ?? "—"}
                  </td>
                </tr>
              ))}
              {!payments?.length && (
                <tr>
                  <td colSpan={5} className="px-3 py-8 text-center text-slate-500 text-sm">
                    No payment records. Run CMS ingestion first.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {payments && payments.length === 50 && (
        <div className="flex items-center gap-3 justify-end">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200 disabled:opacity-30"
          >
            <ChevronLeft className="w-4 h-4" /> Prev
          </button>
          <span className="text-xs text-slate-500">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            className="flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
