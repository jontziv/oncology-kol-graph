import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Sparkles, AlertCircle } from "lucide-react";
import { useExplanation, refreshExplanation } from "@/api/explain";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { cn } from "@/lib/utils";

interface EngagementRationaleProps {
  npi: string;
  compact?: boolean;
}

export function EngagementRationale({ npi, compact = false }: EngagementRationaleProps) {
  const { data, isLoading, isError } = useExplanation(npi);
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshExplanation(npi);
      queryClient.invalidateQueries({ queryKey: ["explain", npi] });
    } finally {
      setRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
        <LoadingSpinner size="sm" />
        <span>Generating engagement rationale...</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex items-center gap-2 text-xs text-rose-400 py-2">
        <AlertCircle className="w-3.5 h-3.5" />
        <span>Could not generate rationale. Check GROQ_API_KEY.</span>
      </div>
    );
  }

  const rationaleText = compact
    ? data.rationale.split(". ").slice(0, 2).join(". ") + "."
    : data.rationale;

  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-1.5 text-xs font-medium text-sky-400">
          <Sparkles className="w-3.5 h-3.5" />
          <span>{data.engagement_type}</span>
          {data.cached && <span className="text-slate-500">(cached)</span>}
        </div>
        {!compact && (
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="text-slate-500 hover:text-slate-300 transition-colors"
            title="Regenerate"
          >
            <RefreshCw className={cn("w-3.5 h-3.5", refreshing && "animate-spin")} />
          </button>
        )}
      </div>

      <p className="text-xs text-slate-300 leading-relaxed">{rationaleText}</p>

      {!compact && (
        <div className="border border-amber-500/20 bg-amber-500/5 rounded p-2 text-xs text-amber-400">
          {data.compliance_note}
        </div>
      )}

      <p className="text-xs text-slate-600 italic">
        AI-generated draft — requires Medical Affairs review before use
      </p>
    </div>
  );
}
