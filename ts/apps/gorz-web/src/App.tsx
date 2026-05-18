import { FileJson, MessageCircle, ShieldCheck, Stethoscope } from "lucide-react";
import { useState } from "react";

import { SafetyBanner } from "./components/SafetyBanner";
import { useGorzApi } from "./state/useGorzApi";
import { DiagnosticsPage } from "./pages/DiagnosticsPage";
import { EvidencePage } from "./pages/EvidencePage";
import { MessengerPage } from "./pages/MessengerPage";
import { SafetyPage } from "./pages/SafetyPage";

type PageId = "messenger" | "diagnostics" | "evidence" | "safety";

const pages = [
  { id: "messenger", label: "Messenger", icon: MessageCircle },
  { id: "diagnostics", label: "Diagnostics", icon: Stethoscope },
  { id: "evidence", label: "Evidence", icon: FileJson },
  { id: "safety", label: "Safety", icon: ShieldCheck },
] satisfies Array<{ id: PageId; label: string; icon: typeof MessageCircle }>;

function App() {
  const api = useGorzApi();
  const [page, setPage] = useState<PageId>("messenger");

  return (
    <div className="app-shell">
      <SafetyBanner error={api.error} health={api.health} safety={api.safety} />
      <nav className="primary-nav" aria-label="Gorz navigation">
        {pages.map((item) => {
          const Icon = item.icon;
          return (
            <button
              aria-current={page === item.id ? "page" : undefined}
              key={item.id}
              onClick={() => setPage(item.id)}
              type="button"
            >
              <Icon aria-hidden="true" size={17} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {api.loading ? <p className="loading-bar">Loading local demo state...</p> : null}

      {page === "messenger" ? <MessengerPage api={api} /> : null}
      {page === "diagnostics" ? (
        <DiagnosticsPage
          diagnostic={api.diagnostic}
          onSelectScenario={api.selectScenario}
          scenarios={api.scenarios}
          selectedScenario={api.selectedScenario}
        />
      ) : null}
      {page === "evidence" ? <EvidencePage incidents={api.incidents} /> : null}
      {page === "safety" ? (
        <SafetyPage audit={api.audit} onPause={api.pause} onResume={api.resume} safety={api.safety} />
      ) : null}
    </div>
  );
}

export default App;

