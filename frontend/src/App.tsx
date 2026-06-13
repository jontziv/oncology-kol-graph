import { Routes, Route } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { NetworkPage } from "@/pages/NetworkPage";
import { InstitutionsPage } from "@/pages/InstitutionsPage";
import { TransparencyPage } from "@/pages/TransparencyPage";
import { KOLProfilePage } from "@/pages/KOLProfilePage";

function DataAttribution() {
  return (
    <footer className="text-xs text-slate-600 px-4 py-2 border-t border-slate-800 flex flex-wrap gap-x-4 gap-y-1">
      <span>Data sources:</span>
      <span>ClinicalTrials.gov (NIH/NLM)</span>
      <span>·</span>
      <span>PubMed (NCBI/NLM)</span>
      <span>·</span>
      <span>CMS Open Payments (CMS.gov)</span>
      <span>·</span>
      <span>NCI SEER Program</span>
      <span className="ml-auto">Portfolio demo · Hypothetical NSCLC launch · Not for clinical use</span>
    </footer>
  );
}

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<NetworkPage />} />
            <Route path="/institutions" element={<InstitutionsPage />} />
            <Route path="/transparency" element={<TransparencyPage />} />
            <Route path="/kols/:npi" element={<KOLProfilePage />} />
          </Routes>
        </main>
        <DataAttribution />
      </div>
    </div>
  );
}
