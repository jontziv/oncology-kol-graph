export function GraphLegend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-slate-400">
      <div className="flex items-center gap-1.5">
        <div className="w-3 h-3 rounded-full bg-sky-400" />
        <span>KOL (size = score)</span>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="w-3 h-3 rounded-full bg-slate-500" />
        <span>Institution</span>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="w-4 h-0.5 bg-amber-400" />
        <span>Co-investigates</span>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="w-4 h-0.5 bg-emerald-500" />
        <span>Co-authored</span>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="w-4 h-0.5 bg-slate-500" />
        <span>Affiliated with</span>
      </div>
    </div>
  );
}
