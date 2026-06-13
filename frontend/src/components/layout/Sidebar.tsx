import { NavLink } from "react-router-dom";
import { Network, Building2, Eye, Dna } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", label: "KOL Network", icon: Network },
  { to: "/institutions", label: "Institutions", icon: Building2 },
  { to: "/transparency", label: "Transparency", icon: Eye },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 flex flex-col bg-slate-900 border-r border-slate-800 min-h-screen">
      <div className="flex items-center gap-2.5 px-4 py-5 border-b border-slate-800">
        <Dna className="w-5 h-5 text-sky-400 shrink-0" />
        <div>
          <div className="text-sm font-semibold text-slate-100 leading-tight">OncologyKOL</div>
          <div className="text-xs text-slate-500">NSCLC Intelligence</div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-sky-500/10 text-sky-400 font-medium"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              )
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-slate-800">
        <div className="text-xs text-slate-600 space-y-0.5">
          <div>Data: ClinicalTrials.gov · PubMed</div>
          <div>CMS Open Payments · NCI SEER</div>
        </div>
      </div>
    </aside>
  );
}
