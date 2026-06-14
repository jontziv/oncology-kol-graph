import { useState } from "react";
import { X, ExternalLink, MapPin, Building2, Check } from "lucide-react";
import { Link } from "react-router-dom";
import { useKOL } from "@/api/kols";
import { useEngagement, useSaveEngagement } from "@/api/engagements";
import { ScoreBadge } from "@/components/shared/ScoreBadge";
import { ConflictBadge } from "@/components/shared/ConflictBadge";
import { EngagementRationale } from "@/components/account/EngagementRationale";
import { LoadingOverlay } from "@/components/shared/LoadingSpinner";
import { cn } from "@/lib/utils";

interface AccountPanelProps {
  npi: string | null;
  onClose: () => void;
}

export function AccountPanel({ npi, onClose }: AccountPanelProps) {
  const { data: kol, isLoading } = useKOL(npi);
  const { data: engagement, refetch } = useEngagement(npi);
  const { mutate: saveEngagement, isPending } = useSaveEngagement();
  const [status, setStatus] = useState<string>(engagement?.status || "To Engage");
  const [notes, setNotes] = useState(engagement?.notes || "");
  const [assignedTo, setAssignedTo] = useState(engagement?.assigned_to || "");
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSubmit = async () => {
    if (!npi) return;
    setSaveSuccess(false);
    saveEngagement(
      {
        npi,
        status: status as "To Engage" | "Engaged" | "Declined",
        notes,
        assigned_to: assignedTo,
      },
      {
        onSuccess: () => {
          setSaveSuccess(true);
          refetch();
          setTimeout(() => setSaveSuccess(false), 3000);
        },
      }
    );
  };

  return (
    <div
      className={cn(
        "fixed right-0 top-0 h-full w-96 bg-slate-900 border-l border-slate-700 shadow-2xl z-50 flex flex-col transition-transform duration-300",
        npi ? "translate-x-0" : "translate-x-full"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
        <span className="text-sm font-semibold text-slate-200">Account Profile</span>
        <button
          onClick={onClose}
          className="text-slate-500 hover:text-slate-300 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto">
        {isLoading || !kol ? (
          <LoadingOverlay label="Loading profile..." />
        ) : (
          <div className="p-4 space-y-5">
            {/* Identity */}
            <div>
              <h2 className="text-base font-semibold text-slate-100">{kol.name}</h2>
              {kol.specialty && (
                <p className="text-xs text-slate-400 mt-0.5">{kol.specialty}</p>
              )}
              <div className="flex flex-wrap gap-3 mt-2 text-xs text-slate-400">
                {kol.institution && (
                  <span className="flex items-center gap-1">
                    <Building2 className="w-3 h-3" />
                    {kol.institution.name}
                  </span>
                )}
                {kol.state && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {kol.city ? `${kol.city}, ` : ""}{kol.state}
                  </span>
                )}
              </div>
            </div>

            {/* Scores */}
            <div className="grid grid-cols-4 gap-2">
              <ScoreBadge label="KOL" score={kol.kol_score} />
              <ScoreBadge label="Trial" score={kol.trial_score} />
              <ScoreBadge label="Pub" score={kol.pub_score} />
              <ScoreBadge label="Geo" score={kol.geographic_reach_score} />
            </div>

            {/* Payments */}
            <div>
              <div className="text-xs font-medium text-slate-400 mb-1.5">
                Disclosed Financial Relationships
              </div>
              <ConflictBadge
                totalUsd={kol.payment_total_usd}
                companyCount={kol.payment_company_count}
              />
              <p className="text-xs text-slate-600 mt-1">(Source: CMS Open Payments)</p>
            </div>

            {/* Engagement Rationale */}
            <div>
              <div className="text-xs font-medium text-slate-400 mb-2">
                Engagement Rationale
              </div>
              <EngagementRationale npi={kol.npi} compact />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-2 text-center">
              {[
                { label: "Trials", value: kol.trials.length },
                { label: "Publications", value: kol.publications.length },
                { label: "States", value: kol.geographic_reach },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-800 rounded p-2">
                  <div className="text-lg font-bold text-slate-100">{value}</div>
                  <div className="text-xs text-slate-500">{label}</div>
                </div>
              ))}
            </div>

            {/* Engagement Tracking - key forces state reset when npi changes */}
            <div key={npi} className="bg-slate-800 rounded-lg p-3 space-y-3">
              <div className="text-xs font-medium text-slate-400">Engagement Tracking</div>

              <div>
                <label className="text-xs text-slate-400 mb-1.5 block">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-100 focus:outline-none focus:border-sky-500"
                >
                  <option>To Engage</option>
                  <option>Engaged</option>
                  <option>Declined</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1.5 block">Assigned To</label>
                <input
                  type="text"
                  value={assignedTo}
                  onChange={(e) => setAssignedTo(e.target.value)}
                  placeholder="Team member name"
                  className="w-full px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1.5 block">Internal Notes</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add notes about this KOL..."
                  rows={3}
                  className="w-full px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 resize-none"
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={isPending}
                className={cn(
                  "w-full py-2 rounded text-xs font-medium transition-all flex items-center justify-center gap-1.5",
                  saveSuccess
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-sky-600 hover:bg-sky-700 disabled:bg-slate-700 text-white border border-sky-600"
                )}
              >
                {isPending ? (
                  <>
                    <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Saving...
                  </>
                ) : saveSuccess ? (
                  <>
                    <Check className="w-4 h-4" />
                    Saved
                  </>
                ) : (
                  "Save Engagement"
                )}
              </button>
            </div>

            {/* Open full profile */}
            <Link
              to={`/kols/${kol.npi}`}
              className="flex items-center justify-center gap-2 w-full py-2 bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-sm rounded-md transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Open Full Profile
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
