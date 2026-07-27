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
  Grid3X3,
  Settings2,
  Key,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyRecord = Record<string, any>;

const AI_PROVIDERS = [
  { id: "openrouter", name: "OpenRouter", keyField: "openrouter_api_key", modelField: "openrouter_model", placeholder: "sk-or-v1-...", defaultModel: "nvidia/nemotron-3-ultra-550b-a55b:free" },
  { id: "openai", name: "OpenAI", keyField: "openai_api_key", modelField: "openai_model", placeholder: "sk-...", defaultModel: "gpt-4o" },
  { id: "anthropic", name: "Anthropic", keyField: "anthropic_api_key", modelField: "anthropic_model", placeholder: "sk-ant-...", defaultModel: "claude-sonnet-4-20250514" },
  { id: "ollama", name: "Ollama (Local)", keyField: "", modelField: "ollama_model", placeholder: "", defaultModel: "llama3" },
  { id: "grok", name: "Grok", keyField: "grok_api_key", modelField: "grok_model", placeholder: "xai-...", defaultModel: "grok-2" },
  { id: "huggingface", name: "HuggingFace", keyField: "huggingface_api_key", modelField: "", placeholder: "hf_...", defaultModel: "" },
];

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
  font_family?: string;
  font_size?: number;
  supports_color?: boolean;
  has_theme?: boolean;
}

interface ThemeConfig {
  primary_color?: string;
  accent_color?: string;
  font_family?: string;
  [key: string]: any;
}

const EXPORT_FORMATS = ["typst", "text", "markdown"] as const;
type Tab = "input" | "preview" | "validation" | "templates" | "history";

export default function ResumeGenerator() {
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [template, setTemplate] = useState("modern");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [, setSelectedTemplate] = useState<Template | null>(null);
  const [templateTheme, setTemplateTheme] = useState<ThemeConfig | null>(null);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [result, setResult] = useState<AnyRecord>({});
  const [currentTab, setCurrentTab] = useState<Tab>("input");
  const [typstSource, setTypstSource] = useState("");
  const [, setCompilationErrors] = useState<string[]>([]);
  const [exportFormat, setExportFormat] = useState<string>("typst");

  // AI Provider settings
  const [aiSettingsOpen, setAiSettingsOpen] = useState(false);
  const [aiProvider, setAiProvider] = useState("openrouter");
  const [aiApiKey, setAiApiKey] = useState("");
  const [aiModel, setAiModel] = useState("nvidia/nemotron-3-ultra-550b-a55b:free");

  useEffect(() => {
    loadTemplates();
    loadVersions();
    loadAiConfig();
  }, []);

  const loadTemplates = async () => {
    try {
      const d = await api.listResumeTemplates();
      setTemplates(d.templates || []);
      if (d.templates?.length > 0) setSelectedTemplate(d.templates[0]);
    } catch {}
  };

  const loadTemplateTheme = async (name: string) => {
    try {
      const d = await api.getResumeTemplateTheme(name);
      setTemplateTheme(d.theme || null);
    } catch {
      setTemplateTheme(null);
    }
  };

  const loadVersions = async () => {
    try {
      const d = await api.listResumeVersions();
      setVersions(d.versions || []);
    } catch {}
  };

  const loadAiConfig = async () => {
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/v1/config/ai");
      if (resp.ok) {
        const config = await resp.json();
        if (config.ai_provider) setAiProvider(config.ai_provider);
        if (config.openrouter_model) setAiModel(config.openrouter_model);
        // API keys are masked, so check localStorage as fallback
        const savedKey = localStorage.getItem(`careerforge_provider_${config.ai_provider || "openrouter"}`);
        if (savedKey) setAiApiKey(savedKey);
      }
    } catch {
      // Backend might not be running yet
    }
  };

  const saveAiConfig = async () => {
    const providerDef = AI_PROVIDERS.find((p) => p.id === aiProvider);
    if (!providerDef) return;
    const payload: Record<string, string> = { ai_provider: aiProvider };
    if (providerDef.keyField && aiApiKey) {
      payload[providerDef.keyField] = aiApiKey;
      localStorage.setItem(`careerforge_provider_${aiProvider}`, aiApiKey);
    }
    if (providerDef.modelField && aiModel) {
      payload[providerDef.modelField] = aiModel;
    }
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/v1/config/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        toast.success(`AI provider set to ${providerDef.name}`);
      } else {
        toast.error("Failed to save AI config");
      }
    } catch {
      toast.error("Could not reach backend");
    }
  };

  const handleTemplateSelect = (name: string) => {
    setTemplate(name);
    loadTemplateTheme(name);
    setCurrentTab("input");
  };

  const handleGenerate = async () => {
    if (!jd.trim()) { toast.error("Paste a job description first"); return; }
    if (jd.length < 20) { toast.error("Job description is too short"); return; }
    setGenerating(true);
    setCurrentTab("preview");
    setCompilationErrors([]);
    try {
      const d = await api.generateResumeFull(jd, template);
      setResult(d);
      toast.success("Resume generated!");
      loadVersions();
      if (d.resume) {
        const typst = await api.renderResumeTemplate(template, d.resume as AnyRecord);
        setTypstSource(typst.typst || "");
      }
    } catch {
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

  const handleExport = async (format: string) => {
    if (!result?.resume) return;
    try {
      let content = "";
      let filename = "";
      let mime = "text/plain";

      if (format === "typst") {
        const d = await api.exportResumeTypst(result.resume as AnyRecord, template);
        content = d.typst;
        filename = "resume.typ";
      } else if (format === "text") {
        const d = await api.exportResumeText(result.resume as AnyRecord);
        content = d.text;
        filename = "resume.txt";
      } else if (format === "markdown") {
        const d = await api.exportResumeMarkdown(result.resume as AnyRecord);
        content = d.markdown;
        filename = "resume.md";
      } else if (format === "json") {
        content = JSON.stringify(result, null, 2);
        filename = "resume.json";
        mime = "application/json";
      }

      const blob = new Blob([content], { type: mime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported as ${format}`);
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
    const sections = result.resume.sections as AnyRecord[] || [];
    return sections
      .sort((a, b) => (a.order as number) - (b.order as number))
      .map((section: AnyRecord) => (
        <div key={section.name as string} className="mb-6">
          <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-3 border-b border-border pb-1">
            {String(section.name)}
          </h3>
          <div className="space-y-1.5">
            {(section.items as AnyRecord[] || []).map((item: AnyRecord, i: number) => (
              <div key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                <span className="text-brand-500 mt-0.5 shrink-0">•</span>
                <span>{String(item.text ?? "")}</span>
              </div>
            ))}
          </div>
        </div>
      ));
  };

  const renderValidation = () => {
    const validation = result?.resume?.validation_report as AnyRecord | null;
    if (!validation) return <p className="text-text-tertiary">No validation data available.</p>;
    const issues = (validation.issues as AnyRecord[]) || [];
    const counts = validation.issues_count as AnyRecord || {};

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-text-primary">{Number(validation.score)}</span>
            <span className="text-sm text-text-secondary">/ 100</span>
          </div>
          <span className={`badge ${validation.passed ? "badge-success" : "badge-warning"}`}>
            {validation.passed ? "Passed" : "Needs work"}
          </span>
          <span className="text-xs text-text-tertiary">{String(counts.error)} errors, {String(counts.warning)} warnings</span>
        </div>
        {issues.length === 0 ? (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">No issues found</span>
          </div>
        ) : (
          <div className="space-y-2">
            {issues.map((issue: AnyRecord, i: number) => (
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
          {[["Role", "target_role"], ["Industry", "target_industry"], ["Strategy", "resume_strategy"], ["Tone", "tone"]].map(([label, key]) => (
            <div key={label} className="card space-y-1">
              <span className="text-xs text-text-tertiary uppercase tracking-wider">{label}</span>
              <p className="font-medium text-text-primary">{String(bp[key] ?? "")}</p>
            </div>
          ))}
        </div>
        {bp.keywords_to_emphasize && (bp.keywords_to_emphasize as string[]).length > 0 && (
          <div className="card">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Keywords</span>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {(bp.keywords_to_emphasize as string[]).slice(0, 20).map((kw: string, i: number) => (
                <span key={i} className="badge-info text-2xs">{kw}</span>
              ))}
            </div>
          </div>
        )}
        {bp.reasoning && (
          <div className="card">
            <span className="text-xs text-text-tertiary uppercase tracking-wider">Strategy Reasoning</span>
            <p className="mt-1 text-sm text-text-secondary">{String(bp.reasoning)}</p>
          </div>
        )}
      </div>
    );
  };

  const renderTemplateGallery = () => (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-text-primary">Template Gallery</h2>
      <p className="text-sm text-text-secondary">Choose a template for your resume. All templates are ATS-friendly.</p>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {templates.map((t) => {
          const isSelected = t.name === template;
          return (
            <button
              key={t.name}
              onClick={() => handleTemplateSelect(t.name)}
              className={`card text-left transition-all duration-200 hover:shadow-elevation-2 ${
                isSelected ? "ring-2 ring-brand-500 border-brand-500" : ""
              }`}
            >
              <div className="space-y-3">
                <div className="flex h-32 w-full items-center justify-center rounded-lg bg-surface-2 border border-border">
                  <FileText className="h-10 w-10 text-text-tertiary" />
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary text-sm">{t.display_name}</h3>
                  <p className="text-xs text-text-tertiary mt-1 line-clamp-2">{t.description || "No description"}</p>
                  <div className="flex items-center gap-3 mt-2 text-2xs text-text-tertiary">
                    <span>{t.font_family || "Default"}</span>
                    <span>{t.page_size}</span>
                    {t.supports_color && <span className="badge badge-success">Color</span>}
                  </div>
                </div>
                {isSelected && <span className="badge badge-success text-xs w-full text-center">Selected</span>}
              </div>
            </button>
          );
        })}
      </div>
      {templateTheme && (
        <div className="card space-y-3">
          <span className="text-xs text-text-tertiary uppercase tracking-wider">Theme Preview</span>
          <div className="flex items-center gap-4">
            {templateTheme.primary_color && (
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded border border-border" style={{ backgroundColor: templateTheme.primary_color }} />
                <span className="text-xs text-text-secondary">Primary</span>
              </div>
            )}
            {templateTheme.accent_color && (
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded border border-border" style={{ backgroundColor: templateTheme.accent_color }} />
                <span className="text-xs text-text-secondary">Accent</span>
              </div>
            )}
            <span className="text-xs text-text-secondary">Font: {templateTheme.font_family}</span>
          </div>
        </div>
      )}
    </div>
  );

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

  // Show loads
  if (generating && !result?.resume) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-center py-16">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-brand-600 mx-auto" />
            <p className="text-text-secondary">Generating your resume...</p>
            <p className="text-xs text-text-tertiary">Parsing job description, analyzing knowledge graph, gathering evidence, and writing content</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Resume Generator</h1>
          <p className="mt-1 text-sm text-text-secondary">Generate ATS-optimized, evidence-backed resumes</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2 flex-wrap">
        {[
          { key: "input", label: "Input", icon: FileText },
          { key: "preview", label: "Preview", icon: Eye },
          { key: "validation", label: "Validation", icon: CheckCircle },
          { key: "templates", label: "Templates", icon: Grid3X3 },
          { key: "history", label: "History", icon: History },
        ].map((tab) => (
          <button key={tab.key} onClick={() => setCurrentTab(tab.key as Tab)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              currentTab === tab.key ? "bg-surface-1 text-brand-600 border-b-2 border-brand-600" : "text-text-secondary hover:text-text-primary"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Input Tab */}
      {currentTab === "input" && (
        <div className="space-y-4">
          {/* AI Provider Settings */}
          <div className="card">
            <button onClick={() => setAiSettingsOpen(!aiSettingsOpen)} className="flex items-center justify-between w-full text-left">
              <div className="flex items-center gap-2">
                <Key className="h-4 w-4 text-text-tertiary" />
                <span className="text-sm font-medium text-text-primary">AI Provider</span>
                <span className="badge badge-info text-2xs">{AI_PROVIDERS.find((p) => p.id === aiProvider)?.name || aiProvider}</span>
              </div>
              {aiSettingsOpen ? <ChevronUp className="h-4 w-4 text-text-tertiary" /> : <ChevronDown className="h-4 w-4 text-text-tertiary" />}
            </button>
            {aiSettingsOpen && (
              <div className="mt-4 space-y-3 border-t border-border pt-4">
                <div className="space-y-1.5">
                  <label className="block text-xs text-text-tertiary">Provider</label>
                  <select value={aiProvider} onChange={(e) => {
                    setAiProvider(e.target.value);
                    const def = AI_PROVIDERS.find((p) => p.id === e.target.value);
                    if (def) setAiModel(def.defaultModel);
                  }} className="input text-sm">
                    {AI_PROVIDERS.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                {AI_PROVIDERS.find((p) => p.id === aiProvider)?.keyField && (
                  <Input label="API Key" type="password" value={aiApiKey} onChange={(e) => setAiApiKey(e.target.value)}
                    placeholder={AI_PROVIDERS.find((p) => p.id === aiProvider)?.placeholder || ""} />
                )}
                <Input label="Model" value={aiModel} onChange={(e) => setAiModel(e.target.value)}
                  placeholder={AI_PROVIDERS.find((p) => p.id === aiProvider)?.defaultModel || ""} />
                <div className="flex justify-end">
                  <Button onClick={saveAiConfig} variant="secondary" size="sm">Save Provider Settings</Button>
                </div>
              </div>
            )}
          </div>

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
                  <select value={template} onChange={(e) => { setTemplate(e.target.value); loadTemplateTheme(e.target.value); }} className="input text-sm py-1.5">
                    {templates.map((t) => (
                      <option key={t.name} value={t.name}>{t.display_name}</option>
                    ))}
                  </select>
                </div>
                {templateTheme?.primary_color && (
                  <div className="h-6 w-6 rounded border border-border mt-5" style={{ backgroundColor: templateTheme.primary_color }} title="Template accent color" />
                )}
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

      {/* Preview Tab */}
      {currentTab === "preview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h2 className="text-lg font-semibold text-text-primary mb-4">Resume Strategy</h2>
            {result?.blueprint ? renderBlueprint() : (
              <EmptyState icon={<FileText className="h-8 w-8" />} title="No blueprint" description="Generate a resume to see the strategy" />
            )}
          </div>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Resume Preview</h2>
              {result?.resume && (
                <div className="flex items-center gap-2">
                  <select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)} className="input text-xs py-1 px-2">
                    {EXPORT_FORMATS.map((f) => <option key={f} value={f}>{f.toUpperCase()}</option>)}
                    <option value="json">JSON</option>
                  </select>
                  <Button variant="ghost" size="sm" onClick={() => handleExport(exportFormat)} icon={<Download className="h-3.5 w-3.5" />}>
                    Export
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleExport("json")} icon={<Settings2 className="h-3.5 w-3.5" />}>
                    JSON
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
            {/* Typst source */}
            {typstSource && (
              <div className="mt-4">
                <details>
                  <summary className="text-xs text-text-tertiary cursor-pointer hover:text-text-secondary">Typst Source ({typstSource.length} chars)</summary>
                  <pre className="mt-2 p-3 rounded-lg bg-surface-2 text-xs text-text-secondary overflow-x-auto max-h-60 overflow-y-auto font-mono">{typstSource}</pre>
                </details>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Validation Tab */}
      {currentTab === "validation" && (
        <div className="max-w-2xl">{renderValidation()}</div>
      )}

      {/* Templates Tab */}
      {currentTab === "templates" && renderTemplateGallery()}

      {/* History Tab */}
      {currentTab === "history" && (
        <div className="max-w-2xl">{renderHistory()}</div>
      )}
    </div>
  );
}
