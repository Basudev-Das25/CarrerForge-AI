import { useEffect, useState } from "react";
import {
  Sparkles,
  FileText,
  Download,
  Eye,
  History,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyRecord = Record<string, any>;

interface ResumeVersion {
  id: string;
  title: string;
  template_name?: string;
  ats_score?: number;
  created_at: string;
}

interface Template {
  name: string;
  display_name: string;
  description: string;
  page_size: string;
}

export default function ResumeGenerator() {
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [template, setTemplate] = useState("modern");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
    const [result, setResult] = useState<AnyRecord>({});
  const [currentTab, setCurrentTab] = useState<"input" | "preview" | "validation" | "history">("input");
  const [typstSource, setTypstSource] = useState("");

  useEffect(() => {
    api.listResumeTemplates().then((d) => setTemplates(d.templates)).catch(() => {});
    loadVersions();
  }, []);

  const loadVersions = async () => {
    try {
      const d = await api.listResumeVersions();
      setVersions(d.versions || []);
    } catch {}
  };

  const handleGenerate = async () => {
    if (!jd.trim()) { toast.error("Paste a job description first"); return; }
    if (jd.length < 20) { toast.error("Job description is too short"); return; }
    setGenerating(true);
    setCurrentTab("preview");
    try {
      const d = await api.generateResumeFull(jd, template);
      setResult(d);
      toast.success("Resume generated!");
      loadVersions();
      // Generate Typst preview
      if (d.resume) {
        const typst = await api.renderResumeTemplate(template, d.resume as AnyRecord);
        setTypstSource(typst.typst || "");
      }
    } catch (e) {
      toast.error("Failed to generate resume");
    } finally {
      setGenerating(false);
    }
  };

  const handleBlueprint = async () => {
    if (!jd.trim()) { toast.error("Paste a job description first"); return; }
    setLoading(true);
    try {
      const d = await api.generateResumeBlueprint(jd);
      setResult({ blueprint: d.blueprint });
      setCurrentTab("preview");
      toast.success("Blueprint generated");
    } catch {
      toast.error("Failed to generate blueprint");
    } finally {
      setLoading(false);
    }
  };

  const handleExportTypst = async () => {
    if (!result?.resume) return;
    try {
      const blob = new Blob([typstSource], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "resume.typ";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Export failed");
    }
  };

  const handleExportText = async () => {
    if (!result?.resume) return;
    try {
      const d = await api.exportResumeText(result.resume as AnyRecord);
      const blob = new Blob([d.text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "resume.txt";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Export failed");
    }
  };

  const loadVersion = async (id: string) => {
    try {
      const d: AnyRecord = await api.getResumeVersion(id);
      const cj = d.content_json as AnyRecord | undefined;
      if (cj?.resume) {
        setResult({ resume: cj.resume, blueprint: cj.blueprint });
        setCurrentTab("preview");
      }
    } catch {
      toast.error("Failed to load version");
    }
  };

  const deleteVersion = async (id: string) => {
    if (!confirm("Delete this version?")) return;
    try {
      await api.deleteResumeVersion(id);
      toast.success("Deleted");
      loadVersions();
    } catch {
      toast.error("Failed to delete");
    }
  };

  const renderSections = () => {
    if (!result?.resume) return null;
    const sections = (result.resume as AnyRecord).sections as Array<AnyRecord> || [];
    return sections
      .sort((a, b) => (a.order as number) - (b.order as number))
      .map((section) => (
        <div key={section.name as string} className="mb-6">
          <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-3 border-b border-border pb-1">
            {section.name as string}
          </h3>
          <div className="space-y-1.5">
            {(section.items as Array<AnyRecord> || []).map((item, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                <span className="text-brand-500 mt-0.5 shrink-0">•</span>
                <span>{(item.text as string) || ""}</span>
              </div>
            ))}
          </div>
        </div>
      ));
  };

  const renderValidation = () => {
    const validation = result?.resume
      ? (result.resume as AnyRecord).validation_report as AnyRecord
      : null;
    if (!validation) return <p className="text-text-tertiary">No validation data available.</p>;
    const issues = (validation.issues as Array<AnyRecord>) || [];
    const counts = validation.issues_count as Record<string, number> || {};

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-text-primary">{validation.score as number}</span>
            <span className="text-sm text-text-secondary">/ 100</span>
          </div>
          <span className={`badge ${validation.passed ? "badge-success" : "badge-warning"}`}>
            {validation.passed ? "Passed" : "Needs work"}
          </span>
          <span className="text-xs text-text-tertiary">{counts.error as number} errors, {counts.warning as number} warnings</span>
        </div>
        {issues.length === 0 ? (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">No issues found</span>
          </div>
        ) : (
          <div className="space-y-2">
            {issues.map((issue, i) => (
              <div key={i} className="flex items-start gap-3 rounded-lg border border-border bg-surface-1 p-3">
                {issue.severity === "error" ? <XCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                  : issue.severity === "warning" ? <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                  : <AlertTriangle className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />}
                <div className="min-w-0">
                  <p className="text-sm text-text-primary">{String(issue.message)}</p>
                  {issue.suggestion && <p className="text-xs text-text-tertiary mt-0.5">{String(issue.suggestion)}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderBlueprint = () => {
    const bp = result?.blueprint as AnyRecord;
    if (!bp) return null;
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="card space-y-1">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Role</span>
            <p className="font-medium text-text-primary">{bp.target_role as string}</p>
          </div>
          <div className="card space-y-1">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Industry</span>
            <p className="font-medium text-text-primary">{bp.target_industry as string}</p>
          </div>
          <div className="card space-y-1">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Strategy</span>
            <p className="font-medium text-text-primary">{bp.resume_strategy as string}</p>
          </div>
          <div className="card space-y-1">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Tone</span>
            <p className="font-medium text-text-primary">{bp.tone as string}</p>
          </div>
        </div>
        {bp.keywords_to_emphasize && (bp.keywords_to_emphasize as string[]).length > 0 && (
          <div className="card">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Keywords</span>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {(bp.keywords_to_emphasize as string[]).slice(0, 20).map((kw, i) => (
                <span key={i} className="badge-info text-2xs">{kw}</span>
              ))}
            </div>
          </div>
        )}
        {bp.reasoning && (
          <div className="card">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Strategy Reasoning</span>
            <p className="mt-1 text-sm text-text-secondary">{bp.reasoning as string}</p>
          </div>
        )}
        {(bp.sections as Array<AnyRecord> || []).length > 0 && (
          <div className="card">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Planned Sections</span>
            <div className="mt-2 space-y-2">
              {(bp.sections as Array<AnyRecord>).map((sec, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-text-primary font-medium">{sec.name as string}</span>
                  <span className="text-text-tertiary">{sec.word_count_target as number} words</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderHistory = () => {
    if (versions.length === 0) {
      return (
        <EmptyState
          icon={<History className="h-8 w-8" />}
          title="No versions yet"
          description="Generate your first resume to see version history"
        />
      );
    }
    return (
      <div className="space-y-3">
        {versions.map((v) => (
          <div key={v.id} className="card-hover flex items-center justify-between">
            <div className="min-w-0 flex-1" onClick={() => loadVersion(v.id)}>
              <h3 className="font-medium text-text-primary truncate">{v.title}</h3>
              <div className="flex items-center gap-3 mt-1 text-xs text-text-tertiary">
                <span>{new Date(v.created_at).toLocaleDateString()}</span>
                {v.template_name && <span>Template: {v.template_name}</span>}
                {v.ats_score != null && (
                  <span className={v.ats_score >= 80 ? "text-green-600" : v.ats_score >= 60 ? "text-amber-600" : "text-red-600"}>
                    ATS: {v.ats_score}
                  </span>
                )}
              </div>
            </div>
            <button onClick={() => deleteVersion(v.id)} className="rounded p-1.5 hover:bg-red-50 text-red-500 ml-2">
              <XCircle className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Resume Generator</h1>
          <p className="mt-1 text-sm text-text-secondary">Generate ATS-optimized, evidence-backed resumes</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {[
          { key: "input", label: "Input", icon: FileText },
          { key: "preview", label: "Preview", icon: Eye },
          { key: "validation", label: "Validation", icon: CheckCircle },
          { key: "history", label: "History", icon: History },
        ].map((tab) => (
          <button key={tab.key} onClick={() => setCurrentTab(tab.key as typeof currentTab)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              currentTab === tab.key ? "bg-surface-1 text-brand-600 border-b-2 border-brand-600" : "text-text-secondary hover:text-text-primary"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {currentTab === "input" && (
        <div className="space-y-4">
          <div className="card space-y-4">
            <h3 className="section-title">Job Description</h3>
            <p className="section-description">Paste the job description you want to tailor your resume for.</p>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              rows={12}
              className="input resize-y min-h-[200px] font-mono text-sm"
              placeholder="Paste the full job description here..."
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-text-tertiary">{jd.length} characters</p>
              <div className="flex items-center gap-3">
                <div className="space-y-1.5">
                  <label className="block text-xs text-text-tertiary">Template</label>
                  <select value={template} onChange={(e) => setTemplate(e.target.value)} className="input text-sm py-1.5">
                    {templates.map((t) => (
                      <option key={t.name} value={t.name}>{t.display_name}</option>
                    ))}
                  </select>
                </div>
                <Button onClick={handleBlueprint} loading={loading} variant="secondary" icon={<FileText className="h-4 w-4" />}>
                  Generate Blueprint
                </Button>
                <Button onClick={handleGenerate} loading={generating} icon={<Sparkles className="h-4 w-4" />}>
                  Generate Resume
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {currentTab === "preview" && (
        <div className="grid grid-cols-2 gap-6">
          {/* Blueprint */}
          <div>
            <h2 className="text-lg font-semibold text-text-primary mb-4">Resume Strategy</h2>
            {result?.blueprint ? renderBlueprint() : (
              <EmptyState icon={<FileText className="h-8 w-8" />} title="No blueprint" description="Generate a resume to see the strategy" />
            )}
          </div>
          {/* Preview */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Resume Preview</h2>
              {result?.resume && (
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={handleExportTypst} icon={<Download className="h-3.5 w-3.5" />}>
                    Typst
                  </Button>
                  <Button variant="ghost" size="sm" onClick={handleExportText} icon={<Download className="h-3.5 w-3.5" />}>
                    Text
                  </Button>
                </div>
              )}
            </div>
            {result?.resume ? (
              <div className="card max-h-[80vh] overflow-y-auto">
                {renderSections()}
              </div>
            ) : (
              <EmptyState icon={<Eye className="h-8 w-8" />} title="No resume yet" description="Generate a resume to see the preview" />
            )}
          </div>
        </div>
      )}

      {currentTab === "validation" && (
        <div className="max-w-2xl">{renderValidation()}</div>
      )}

      {currentTab === "history" && (
        <div className="max-w-2xl">{renderHistory()}</div>
      )}

      {generating && !result && (
        <div className="flex items-center justify-center py-16">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-brand-600 mx-auto" />
            <p className="text-text-secondary">Generating your resume...</p>
            <p className="text-xs text-text-tertiary">Parsing job description, analyzing knowledge graph, gathering evidence, and writing content</p>
          </div>
        </div>
      )}
    </div>
  );
}
