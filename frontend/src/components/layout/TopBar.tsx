import { useLocation } from "react-router-dom";

const PAGE_TITLES: Record<string, string> = {
  "/": "KOL Network",
  "/institutions": "Institution Rankings",
  "/transparency": "Open Payments Transparency",
};

export function TopBar() {
  const { pathname } = useLocation();
  const base = "/" + pathname.split("/")[1];
  const title = PAGE_TITLES[base] ?? "KOL Profile";

  return (
    <header className="h-12 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
      <h1 className="text-sm font-semibold text-slate-200">{title}</h1>
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700 text-sky-400 font-mono">
          NSCLC
        </span>
        <span>Hypothetical launch · portfolio demo</span>
      </div>
    </header>
  );
}
