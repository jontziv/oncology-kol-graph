import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut } from "lucide-react";

const PAGE_TITLES: Record<string, string> = {
  "/": "KOL Network",
  "/institutions": "Institution Rankings",
  "/transparency": "Open Payments Transparency",
};

export function TopBar() {
  const { pathname } = useLocation();
  const { session, logOut } = useAuth();
  const navigate = useNavigate();
  const base = "/" + pathname.split("/")[1];
  const title = PAGE_TITLES[base] ?? "KOL Profile";

  const handleLogOut = async () => {
    await logOut();
    navigate("/login");
  };

  return (
    <header className="h-12 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
      <h1 className="text-sm font-semibold text-slate-200">{title}</h1>
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700 text-sky-400 font-mono">
            NSCLC
          </span>
          <span>Hypothetical launch · portfolio demo</span>
        </div>
        {session && (
          <div className="flex items-center gap-3 border-l border-slate-700 pl-3">
            <span className="text-slate-400">{session.user.email}</span>
            <button
              onClick={handleLogOut}
              className="text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1"
              title="Log out"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Log out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
