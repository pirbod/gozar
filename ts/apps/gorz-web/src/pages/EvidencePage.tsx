import { IncidentExportPanel } from "../components/IncidentExportPanel";

interface EvidencePageProps {
  incidents: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["incidents"];
}

export function EvidencePage({ incidents }: EvidencePageProps) {
  return <IncidentExportPanel incidents={incidents} />;
}

