import { useState, useRef, useEffect } from "react";
import { useKOLs } from "@/api/kols";
import { useGraph, useKOLNetwork } from "@/api/graph";
import { KOLTable } from "@/components/kol/KOLTable";
import { KOLGraph } from "@/components/graph/KOLGraph";
import { GraphLegend } from "@/components/graph/GraphLegend";
import { FilterBar } from "@/components/shared/FilterBar";
import { AccountPanel } from "@/components/account/AccountPanel";
import { LoadingOverlay } from "@/components/shared/LoadingSpinner";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { KOLFilters } from "@/types";

const DEFAULT_FILTERS: KOLFilters = { state: "", minScore: 0, phase: "", recruitingOnly: false };

export function NetworkPage() {
  const [filters, setFilters] = useState<KOLFilters>(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("kol_score");
  const [selectedNpi, setSelectedNpi] = useState<string | null>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [graphSize, setGraphSize] = useState({ width: 800, height: 600 });

  const { data: kolList, isLoading: listLoading } = useKOLs(page, filters, sortBy);
  const { data: fullGraph, isLoading: graphLoading } = useGraph(filters.minScore, filters.state);
  const { data: networkGraph } = useKOLNetwork(selectedNpi);

  const activeGraph = selectedNpi && networkGraph ? networkGraph : fullGraph;

  useEffect(() => {
    const el = graphContainerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setGraphSize({ width, height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const handleSortChange = (field: string) => {
    setSortBy(field);
    setPage(1);
  };

  const handleFilterChange = (f: KOLFilters) => {
    setFilters(f);
    setPage(1);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-48px)]">
      <div className="px-4 pt-4 pb-3">
        <FilterBar filters={filters} onChange={handleFilterChange} />
      </div>

      <div className="flex flex-1 overflow-hidden gap-0">
        {/* Left panel: KOL table */}
        <div className="w-72 shrink-0 flex flex-col border-r border-slate-800 overflow-hidden">
          <div className="px-3 py-2 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              {kolList ? `${kolList.total} investigators` : "Loading..."}
            </span>
          </div>
          {listLoading ? (
            <LoadingOverlay label="Loading investigators..." />
          ) : (
            <KOLTable
              kols={kolList?.items ?? []}
              selectedNpi={selectedNpi}
              onSelect={setSelectedNpi}
              onSortChange={handleSortChange}
              sortBy={sortBy}
              className="flex-1"
            />
          )}
          {/* Pagination */}
          {kolList && kolList.total > 20 && (
            <div className="flex items-center justify-between px-3 py-2 border-t border-slate-800">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="text-slate-400 hover:text-slate-200 disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-slate-500">
                {page} / {Math.ceil(kolList.total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(kolList.total / 20)}
                className="text-slate-400 hover:text-slate-200 disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Right panel: graph */}
        <div className="flex-1 flex flex-col overflow-hidden relative" ref={graphContainerRef}>
          {graphLoading ? (
            <LoadingOverlay label="Building graph..." />
          ) : activeGraph ? (
            <>
              <KOLGraph
                data={activeGraph}
                onNodeClick={setSelectedNpi}
                highlightNpi={selectedNpi}
                width={graphSize.width}
                height={graphSize.height - 36}
              />
              <div className="absolute bottom-3 left-3 px-3 py-2 bg-slate-900/80 backdrop-blur rounded-lg border border-slate-700">
                <GraphLegend />
              </div>
              {selectedNpi && (
                <div className="absolute top-3 left-3 text-xs text-slate-400 bg-slate-900/80 backdrop-blur px-2 py-1 rounded border border-slate-700">
                  Showing 1-hop network for selected KOL
                  <button
                    onClick={() => setSelectedNpi(null)}
                    className="ml-2 text-sky-400 hover:text-sky-300"
                  >
                    Show all
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500 text-sm">
              No data. Run ingestion scripts first.
            </div>
          )}
        </div>
      </div>

      {/* Account panel slide-in */}
      <AccountPanel npi={selectedNpi} onClose={() => setSelectedNpi(null)} />
      {selectedNpi && (
        <div
          className="fixed inset-0 bg-black/30 z-40"
          onClick={() => setSelectedNpi(null)}
        />
      )}
    </div>
  );
}
