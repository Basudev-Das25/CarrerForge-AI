import { ExternalLink, Bug, Lightbulb, MessageCircle, BookOpen, Download } from "lucide-react";
import { Button } from "@/components/common/Button";
import { api } from "@/services/api";
import { useState } from "react";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */

export default function Feedback() {
  const [exporting, setExporting] = useState(false);

  const handleExportDiagnostics = async () => {
    setExporting(true);
    try {
      const d = await api.exportDiagnostics();
      toast.success(`Diagnostics exported to ${(d as any).path}`);
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  };

  const openUrl = (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const links = [
    { icon: Bug, label: "Report a Bug", url: "https://github.com/Basudev-Das/CareerForge-AI/issues/new?template=bug_report.md", color: "text-red-500" },
    { icon: Lightbulb, label: "Request a Feature", url: "https://github.com/Basudev-Das/CareerForge-AI/issues/new?template=feature_request.md", color: "text-amber-500" },
    { icon: MessageCircle, label: "Join the Discussion", url: "https://github.com/Basudev-Das/CareerForge-AI/discussions", color: "text-blue-500" },
    { icon: BookOpen, label: "Documentation", url: "https://github.com/Basudev-Das/CareerForge-AI/tree/main/docs", color: "text-green-500" },
    { icon: ExternalLink, label: "GitHub Repository", url: "https://github.com/Basudev-Das/CareerForge-AI", color: "text-purple-500" },
  ];

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Help & Feedback</h1>
        <p className="mt-1 text-sm text-text-secondary">Get help or share feedback with the team</p>
      </div>

      <div className="card space-y-3">
        <h3 className="section-title">Quick Links</h3>
        <div className="space-y-2">
          {links.map((link) => (
            <button key={link.label} onClick={() => openUrl(link.url)}
              className="w-full flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-surface-2 transition-colors text-left">
              <link.icon className={`h-5 w-5 ${link.color} shrink-0`} />
              <span className="text-sm text-text-primary">{link.label}</span>
              <ExternalLink className="h-3.5 w-3.5 text-text-tertiary ml-auto" />
            </button>
          ))}
        </div>
      </div>

      <div className="card space-y-3">
        <h3 className="section-title">Diagnostics</h3>
        <p className="text-sm text-text-secondary">
          Export diagnostic information to help troubleshoot issues. API keys are automatically redacted.
        </p>
        <Button onClick={handleExportDiagnostics} loading={exporting} variant="secondary" icon={<Download className="h-4 w-4" />}>
          Export Diagnostics
        </Button>
      </div>
    </div>
  );
}
