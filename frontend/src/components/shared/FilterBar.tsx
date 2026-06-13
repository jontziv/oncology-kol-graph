import { type KOLFilters } from "@/types";

const US_STATES = [
  "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
  "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
  "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
  "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
  "New Hampshire","New Jersey","New Mexico","New York","North Carolina",
  "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
  "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
  "Virginia","Washington","West Virginia","Wisconsin","Wyoming",
];

interface FilterBarProps {
  filters: KOLFilters;
  onChange: (filters: KOLFilters) => void;
}

export function FilterBar({ filters, onChange }: FilterBarProps) {
  return (
    <div className="flex flex-wrap gap-3 p-3 bg-slate-800/50 border border-slate-700 rounded-lg">
      <select
        value={filters.state}
        onChange={(e) => onChange({ ...filters, state: e.target.value })}
        className="bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-sky-500"
      >
        <option value="">All states</option>
        {US_STATES.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-400 whitespace-nowrap">
          Min score: <span className="text-slate-200 font-medium">{filters.minScore}</span>
        </label>
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={filters.minScore}
          onChange={(e) => onChange({ ...filters, minScore: Number(e.target.value) })}
          className="w-24 accent-sky-400"
        />
      </div>

      <select
        value={filters.phase}
        onChange={(e) => onChange({ ...filters, phase: e.target.value })}
        className="bg-slate-700 border border-slate-600 text-slate-200 text-sm rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-sky-500"
      >
        <option value="">All phases</option>
        <option value="Phase 1">Phase 1</option>
        <option value="Phase 2">Phase 2</option>
        <option value="Phase 3">Phase 3</option>
      </select>

      <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={filters.recruitingOnly}
          onChange={(e) => onChange({ ...filters, recruitingOnly: e.target.checked })}
          className="accent-sky-400 w-4 h-4"
        />
        Recruiting only
      </label>

      {(filters.state || filters.minScore > 0 || filters.phase || filters.recruitingOnly) && (
        <button
          onClick={() => onChange({ state: "", minScore: 0, phase: "", recruitingOnly: false })}
          className="text-xs text-sky-400 hover:text-sky-300 underline ml-auto"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
