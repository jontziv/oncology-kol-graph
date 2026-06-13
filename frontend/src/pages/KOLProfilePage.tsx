import { useParams, Link } from "react-router-dom";
import { useKOL } from "@/api/kols";
import { LoadingOverlay } from "@/components/shared/LoadingSpinner";
import { ScoreBadge } from "@/components/shared/ScoreBadge";
import { ConflictBadge } from "@/components/shared/ConflictBadge";
import { EngagementRationale } from "@/components/account/EngagementRationale";
import { formatCurrency } from "@/lib/utils";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { ArrowLeft, ExternalLink, MapPin, Building2 } from "lucide-react";

export function KOLProfilePage() {
  const { npi } = useParams<{ npi: string }>();
  const { data: kol, isLoading } = useKOL(npi ?? null);

  if (isLoading) return <LoadingOverlay label="Loading profile..." />;
  if (!kol) return (
    <div className="p-6 text-slate-400 text-sm">
      Investigator not found.{" "}
      <Link to="/" className="text-sky-400 hover:underline">Back to network</Link>
    </div>
  );

  const scoreData = [
    { axis: "Trial", value: kol.trial_score },
    { axis: "Publication", value: kol.pub_score },
    { axis: "Activity", value: kol.activity_score },
    { axis: "Geographic", value: kol.geographic_reach_score },
  ];

  // Aggregate payments by year for bar chart
  const paymentsByYear: Record<number, number> = {};
  for (const p of kol.payments) {
    if (p.year) paymentsByYear[p.year] = (paymentsByYear[p.year] ?? 0) + p.amount_usd;
  }
  const paymentChartData = Object.entries(paymentsByYear)
    .map(([year, total]) => ({ year, total }))
    .sort((a, b) => Number(a.year) - Number(b.year));

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Back */}
      <Link to="/" className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200">
        <ArrowLeft className="w-4 h-4" />
        Back to Network
      </Link>

      {/* Header */}
      <div className="flex items-start gap-6">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-100">{kol.name}</h1>
          {kol.specialty && (
            <p className="text-sm text-slate-400 mt-1">{kol.specialty}</p>
          )}
          <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-400">
            {kol.institution && (
              <span className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4" />
                {kol.institution.name}
              </span>
            )}
            {kol.state && (
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4" />
                {kol.city ? `${kol.city}, ` : ""}{kol.state}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-4">
          <ScoreBadge label="KOL Score" score={kol.kol_score} />
          <ScoreBadge label="Trial" score={kol.trial_score} />
          <ScoreBadge label="Publication" score={kol.pub_score} />
          <ScoreBadge label="Activity" score={kol.activity_score} />
          <ScoreBadge label="Geographic" score={kol.geographic_reach_score} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Score radar */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Score Breakdown</h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={scoreData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="axis" tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <Radar name="Score" dataKey="value" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* AI Engagement Rationale */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Engagement Rationale</h3>
          <EngagementRationale npi={kol.npi} />
        </div>
      </div>

      {/* Payments */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-300">
            Disclosed Financial Relationships
          </h3>
          <ConflictBadge totalUsd={kol.payment_total_usd} companyCount={kol.payment_company_count} />
        </div>
        <p className="text-xs text-slate-500 mb-3">
          Source: CMS Open Payments (public database). Disclosure does not indicate wrongdoing.
        </p>
        {paymentChartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={paymentChartData} barSize={24}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                formatter={(v) => formatCurrency(Number(v))}
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6, fontSize: 12 }}
              />
              <Bar dataKey="total" fill="#38bdf8" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-slate-500">No payment records on file.</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Trials */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">
            NSCLC Trials ({kol.trials.length})
          </h3>
          {kol.trials.length === 0 ? (
            <p className="text-xs text-slate-500">No trials on record.</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {kol.trials.map((t) => (
                <div key={t.nct_id} className="border border-slate-700 rounded p-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs text-slate-200 leading-snug flex-1">{t.title ?? t.nct_id}</p>
                    <a
                      href={`https://clinicaltrials.gov/study/${t.nct_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sky-400 shrink-0"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <div className="flex gap-2 mt-1.5 text-xs text-slate-500">
                    <span>{t.phase}</span>
                    <span>·</span>
                    <span className={t.status?.includes("Recruiting") ? "text-emerald-400" : ""}>
                      {t.status}
                    </span>
                    {t.role && <><span>·</span><span>{t.role}</span></>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Publications */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">
            Publications ({kol.publications.length})
          </h3>
          {kol.publications.length === 0 ? (
            <p className="text-xs text-slate-500">No publications matched.</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {kol.publications.map((p) => (
                <div key={p.pmid} className="border border-slate-700 rounded p-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs text-slate-200 leading-snug flex-1">{p.title ?? p.pmid}</p>
                    <a
                      href={`https://pubmed.ncbi.nlm.nih.gov/${p.pmid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sky-400 shrink-0"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <div className="flex gap-2 mt-1.5 text-xs text-slate-500">
                    <span>{p.journal}</span>
                    {p.year && <><span>·</span><span>{p.year}</span></>}
                    <span>·</span>
                    <span>{p.citation_count} citations</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
