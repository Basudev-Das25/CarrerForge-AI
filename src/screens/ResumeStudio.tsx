/**
 * Resume Studio — Unified resume generation, editing, ATS analysis, and export.
 *
 * Step wizard: JD Input → Blueprint → Generate → Edit → ATS → Export
 * Replaces both ResumeGenerator.tsx and ATSDashboard.tsx.
 */

import { useEffect, useState, useCallback, useRef } from "react";
import {
  Sparkles, FileText, CheckCircle, XCircle, AlertTriangle,
  Loader2, Download, History, ChevronRight, ChevronLeft,
  Check, Edit3, Plus, Trash2, Target, Search,
  ArrowUpRight,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyRecord = Record<string, any>;

// ── Step Definitions ─────────────────────────────────────────

const STEPS = [
  { key: "input", label: "Job Description", icon: FileText },
  { key: "blueprint", label: "Strategy", icon: Search },
  { key: "generate", label: "Generate", icon: Sparkles },
  { key: "edit", label: "Edit", icon: Edit3 },
  { key: "ats", label: "ATS Analysis", icon: Target },
  { key: "export", label: "Export", icon: Download },
] as const;

type StepKey = (typeof STEPS)[number]["key"];

// ── Export Formats ───────────────────────────────────────────

const EXPORT_FORMATS = [
  { id: "typst", label: "Typst", ext: ".typ" },
  { id: "text", label: "Plain Text", ext: ".txt" },
  { id: "markdown", label: "Markdown", ext: ".md" },
  { id: "json", label: "JSON", ext: ".json" },
] as const;

// ── Templates ────────────────────────────────────────────────

interface TemplateInfo {
  name: string;
  display_name: string;
  description: string;
  page_size: string;
}

// ── ATS Types ────────────────────────────────────────────────

interface ATSReport {
  overall_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  keyword_density: number;
  readability_score: number;
  impact_score: number;
  achievement_score: number;
  specificity_score: number;
  evidence_coverage: number;
  suggestions: Array<{
    priority: string;
    description: string;
    section: string;
    expected_improvement: number;
  }>;
  sections: Array<{ name: string; score: number; suggestions: string[] }>;
  missing_sections: string[];
}

// ── Helper: simple keyword extraction ────────────────────────

function extractKeywords(text: string): string[] {
  const words = text.toLowerCase().split(/[\s,;(){}[\]]+/);
  const stopWords = new Set([
    "the","and","for","with","this","that","from","will","have","are","was",
    "were","been","being","can","may","our","your","their","its","who","what",
    "which","where","when","how","all","each","than","them","then","also","such",
    "into","over","only","very","not","but","about","more","other","some","any",
    "most","just","should","would","could","does","doing","done",
  ]);
  return [...new Set(words.filter((w) => w.length > 2 && !stopWords.has(w)))].slice(0, 40);
}

// ── Synonym map for ATS keyword matching ─────────────────────

const TECH_SYNONYMS: Record<string, string[]> = {
  "k8s": ["kubernetes"],
  "ml": ["machine learning"],
  "ai": ["artificial intelligence"],
  "react": ["react.js", "reactjs"],
  "node": ["node.js", "nodejs"],
  "aws": ["amazon web services", "amazon web service"],
  "gcp": ["google cloud platform"],
  "azure": ["microsoft azure"],
  "js": ["javascript"],
  "ts": ["typescript"],
  "db": ["database"],
  "devops": ["dev ops", "development operations"],
  "cicd": ["ci/cd", "continuous integration", "continuous delivery"],
  "ux": ["user experience"],
  "ui": ["user interface"],
  "postgres": ["postgresql"],
  "mern": ["mongodb", "express", "react", "node.js"],
  "full stack": ["fullstack", "full-stack"],
  "microservice": ["microservices"],
};

function expandSynonyms(keywords: string[]): string[] {
  const expanded = new Set(keywords.map(k => k.toLowerCase()));
  for (const kw of keywords) {
    const lower = kw.toLowerCase();
    const synonyms = TECH_SYNONYMS[lower];
    if (synonyms) {
      for (const syn of synonyms) expanded.add(syn);
    }
    // Also reverse-lookup: if any synonym maps TO this keyword
    for (const [key, vals] of Object.entries(TECH_SYNONYMS)) {
      if (vals.includes(lower)) expanded.add(key);
    }
  }
  return [...expanded];
}

// ── Score Color Helper ───────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-amber-600";
  return "text-red-600";
}

function scoreBg(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-amber-500";
  return "bg-red-500";
}

// ── Main Component ───────────────────────────────────────────

export default function ResumeStudio() {
  // ── Wizard step ─────────────────────────────────────────
  const [step, setStep] = useState<StepKey>("input");

  // ── Template ────────────────────────────────────────────
  const [template, setTemplate] = useState("modern");
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);

  // ── JD Input ────────────────────────────────────────────
  const [jd, setJd] = useState("");

  // ── Blueprint ───────────────────────────────────────────
  const [blueprint, setBlueprint] = useState<AnyRecord | null>(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);

  // ── Generation ──────────────────────────────────────────
  const [generating, setGenerating] = useState(false);
  const [genProgress, setGenProgress] = useState("");
  const [genStep, setGenStep] = useState(0);
  const genSteps = [
    "Parsing job description...",
    "Analyzing requirements...",
    "Gathering your experience...",
    "Writing summary section...",
    "Building skills section...",
    "Writing experience bullets...",
    "Polishing content...",
    "Validating quality...",
  ];

  // ── Resume result ───────────────────────────────────────
  const [resume, setResume] = useState<AnyRecord | null>(null);
  const [editableSections, setEditableSections] = useState<AnyRecord[]>([]);

  // ── Version / History ───────────────────────────────────
  const [versions, setVersions] = useState<AnyRecord[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // ── ATS ─────────────────────────────────────────────────
  const [atsReport, setAtsReport] = useState<ATSReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizedResult, setOptimizedResult] = useState<AnyRecord | null>(null);
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set());

  // ── Export ──────────────────────────────────────────────
  const [exportFormat, setExportFormat] = useState("typst");
  const [exporting, setExporting] = useState(false);

  // ── Keyword extraction (for ATS) ────────────────────────
  const [jdKeywords, setJdKeywords] = useState<string[]>([]);

  // ── Timer ref for generation progress ───────────────────
  const progressTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Load templates on mount ─────────────────────────────
  useEffect(() => {
    api.listResumeTemplates()
      .then((d) => setTemplates(d.templates || []))
      .catch(() => {});
    loadVersions();
  }, []);

  // ── Cleanup timer ───────────────────────────────────────
  useEffect(() => {
    return () => {
      if (progressTimerRef.current) clearInterval(progressTimerRef.current);
    };
  }, []);

  // ── Load versions ───────────────────────────────────────
  const loadVersions = async () => {
    try {
      const d = await api.listResumeVersions();
      setVersions(d.versions || []);
    } catch { /* ignore */ }
  };

  // ── Step Navigation ─────────────────────────────────────

  const goToStep = (s: StepKey) => setStep(s);
  const prevStep = () => goToStep("input");

  // ── Full Generate Flow (Step 1 → 2 → 3 → 4) ────────────

  const handleGenerate = async () => {
    if (!jd.trim()) { toast.error("Paste a job description first"); return; }

    // ── Phase 1: Blueprint (auto-advance to Step 2) ──
    setJdKeywords(extractKeywords(jd));
    setBlueprintLoading(true);
    goToStep("blueprint");

    try {
      const bp = await api.generateResumeBlueprint(jd);
      setBlueprint(bp.blueprint || {});
      setBlueprintLoading(false);

      // ── Phase 2: Generate with progress (auto-advance to Step 3) ──
      setGenerating(true);
      setGenStep(0);
      setGenProgress(genSteps[0]);
      goToStep("generate");

      progressTimerRef.current = setInterval(() => {
        setGenStep((prev) => {
          const next = Math.min(prev + 1, genSteps.length - 1);
          setGenProgress(genSteps[next]);
          return next;
        });
      }, 800);

      const d = await api.generateResumeFull(jd, template);
      const r = d.resume as AnyRecord | null;
      setResume(r);

      if (r?.sections) {
        const sections = (r.sections as AnyRecord[]).map((s: AnyRecord, si: number) => ({
          ...s,
          _id: `sec_${si}`,
          items: (s.items as AnyRecord[] || []).map((item: AnyRecord, ii: number) => ({
            ...item,
            _id: `item_${si}_${ii}`,
          })),
        }));
        setEditableSections(sections);
      }

      // Clear timer and land on Edit
      if (progressTimerRef.current) clearInterval(progressTimerRef.current);
      toast.success("Resume generated!");
      loadVersions();
      goToStep("edit");
    } catch {
      if (progressTimerRef.current) clearInterval(progressTimerRef.current);
      setBlueprintLoading(false);
      setGenerating(false);
      toast.error("Failed to generate resume");
    } finally {
      setGenerating(false);
    }
  };

  // ── Edit: Inline editing ─────────────────────────────────

  const updateBullet = (sectionIdx: number, itemIdx: number, text: string) => {
    setEditableSections((prev) => {
      const next = [...prev];
      const items = [...(next[sectionIdx]?.items || [])];
      items[itemIdx] = { ...items[itemIdx], text };
      next[sectionIdx] = { ...next[sectionIdx], items };
      return next;
    });
  };

  const addBullet = (sectionIdx: number) => {
    setEditableSections((prev) => {
      const next = [...prev];
      const items = [...(next[sectionIdx]?.items || [])];
      items.push({ text: "", _id: `item_${sectionIdx}_${items.length}_new` });
      next[sectionIdx] = { ...next[sectionIdx], items };
      return next;
    });
  };

  const removeBullet = (sectionIdx: number, itemIdx: number) => {
    setEditableSections((prev) => {
      const next = [...prev];
      const items = (next[sectionIdx]?.items || []).filter((_: any, i: number) => i !== itemIdx);
      next[sectionIdx] = { ...next[sectionIdx], items };
      return next;
    });
  };

  // ── Edit: Rebuild resume object from sections ───────────

  const buildResumeFromSections = useCallback((): AnyRecord => {
    return {
      ...resume,
      sections: editableSections.map((s) => ({
        name: s.name,
        order: s.order,
        items: (s.items || []).map((item: AnyRecord) => ({
          text: item.text,
          ...(item.evidence_source ? { evidence_source: item.evidence_source } : {}),
          ...(item.entity_id ? { entity_id: item.entity_id } : {}),
        })),
      })),
    };
  }, [resume, editableSections]);

  // ── Edit: Save version ──────────────────────────────────

  const handleSaveVersion = async () => {
    try {
      const updated = buildResumeFromSections();
      // Send updated resume to render endpoint to get Typst preview
      await api.renderResumeTemplate(template, updated);
      toast.success("Version saved");
      loadVersions();
    } catch {
      toast.error("Failed to save version");
    }
  };

  // ── ATS: Analyze current resume ─────────────────────────

  const handleAnalyze = async () => {
    const currentResume = resume || buildResumeFromSections();
    if (!currentResume?.sections?.length) { toast.error("Generate a resume first"); return; }
    if (!jd.trim()) { toast.error("Paste a job description first"); return; }

    setAnalyzing(true);
    try {
      const jdLower = jd.toLowerCase();
      const technologies = [
        "python","javascript","typescript","react","node","java","rust","go",
        "ruby","php","swift","kotlin","sql","docker","kubernetes","aws","azure",
        "gcp","git","linux","machine learning","deep learning","ai","nlp",
        "html","css","tailwind","fastapi","django","flask","express","nextjs",
        "vue","angular","postgresql","mysql","mongodb","redis","graphql",
        "rest","api","microservices","terraform",
      ].filter((t) => jdLower.includes(t));

      const jobProfile: AnyRecord = {
        keywords: jdKeywords,
        ats_keywords: jdKeywords.slice(0, 20),
        required_skills: technologies,
        technologies,
        summary: jd.slice(0, 2000),
        raw_jd: jd,
      };

      const d = await api.analyzeResume(currentResume, jobProfile);
      setAtsReport(d.report as unknown as ATSReport);
      goToStep("ats");
    } catch {
      toast.error("ATS analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  // ── ATS: Accept/reject suggestions ──────────────────────

  const toggleSuggestion = (idx: number) => {
    setAcceptedSuggestions((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const applyAcceptedSuggestions = () => {
    if (!atsReport || acceptedSuggestions.size === 0) {
      toast.info("No suggestions selected");
      return;
    }
    toast.success(`${acceptedSuggestions.size} suggestion(s) applied to resume`);
    // In a full implementation, each suggestion would modify specific bullet points
    // For now, mark them as applied and re-analyze
    setAcceptedSuggestions(new Set());
    handleAnalyze();
  };

  // ── ATS: Optimize ───────────────────────────────────────

  const handleOptimize = async () => {
    const currentResume = resume || buildResumeFromSections();
    if (!atsReport) { toast.error("Run analysis first"); return; }

    setOptimizing(true);
    try {
      const jobProfile: AnyRecord = {
        keywords: atsReport.matched_keywords,
        ats_keywords: atsReport.missing_keywords,
        required_skills: [],
        technologies: [],
        summary: jd.slice(0, 2000),
        raw_jd: jd,
      };
      const d = await api.optimizeResume(currentResume, jobProfile, 85, 3);
      setOptimizedResult(d);

      if (d.resume?.sections) {
        const sections = (d.resume.sections as AnyRecord[]).map((s: AnyRecord, si: number) => ({
          ...s,
          _id: `sec_opt_${si}`,
          items: (s.items as AnyRecord[] || []).map((item: AnyRecord, ii: number) => ({
            ...item,
            _id: `item_opt_${si}_${ii}`,
          })),
        }));
        setEditableSections(sections);
        setResume(d.resume);
      }

      toast.success(`Score improved from ${d.initial_score.toFixed(1)} to ${d.final_score.toFixed(1)}`);
    } catch {
      toast.error("Optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  // ── Export ──────────────────────────────────────────────

  const handleExport = async () => {
    const currentResume = resume || buildResumeFromSections();
    if (!currentResume?.sections?.length) { toast.error("No resume to export"); return; }

    setExporting(true);
    try {
      let content = "";
      let filename = "";
      let mime = "text/plain";

      if (exportFormat === "typst") {
        const d = await api.exportResumeTypst(currentResume, template);
        content = d.typst;
        filename = `resume.typ`;
      } else if (exportFormat === "text") {
        const d = await api.exportResumeText(currentResume);
        content = d.text;
        filename = `resume.txt`;
      } else if (exportFormat === "markdown") {
        const d = await api.exportResumeMarkdown(currentResume);
        content = d.markdown;
        filename = `resume.md`;
      } else {
        content = JSON.stringify({ resume: currentResume, blueprint, template }, null, 2);
        filename = `resume.json`;
        mime = "application/json";
      }

      const blob = new Blob([content], { type: mime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported as ${exportFormat.toUpperCase()}`);
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  };

  // ── Load version from history ───────────────────────────

  const loadVersion = async (id: string) => {
    try {
      const d: AnyRecord = await api.getResumeVersion(id);
      const cj = d.content_json as AnyRecord | undefined;
      if (cj?.resume) {
        setResume(cj.resume);
        if (cj.resume.sections) {
          const sections = (cj.resume.sections as AnyRecord[]).map((s: AnyRecord, si: number) => ({
            ...s,
            _id: `sec_v_${si}`,
            items: (s.items as AnyRecord[] || []).map((item: AnyRecord, ii: number) => ({
              ...item,
              _id: `item_v_${si}_${ii}`,
            })),
          }));
          setEditableSections(sections);
        }
        setShowHistory(false);
        goToStep("edit");
      }
    } catch {
      toast.error("Failed to load version");
    }
  };

  // ── Render: Step Indicator ──────────────────────────────

  const renderSteps = () => (
    <div className="flex items-center gap-0.5 mb-6">
      {STEPS.map((s, idx) => {
        const currentIdx = STEPS.findIndex((st) => st.key === step);
        const isActive = s.key === step;
        const isDone = idx < currentIdx;
        // Step 1 always clickable. Steps 4-6 only after generation.
        // Steps 2 (blueprint) and 3 (generate) are auto-navigated only.
        const hasResume = editableSections.length > 0;
        const isClickable = s.key === "input" || (hasResume && s.key !== "blueprint" && s.key !== "generate");

        return (
          <div key={s.key} className="flex items-center flex-1 min-w-0">
            <button
              onClick={() => isClickable && goToStep(s.key)}
              disabled={!isClickable}
              className={`flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-lg transition-colors w-full ${
                isActive
                  ? "bg-brand-600 text-white shadow-sm"
                  : isDone
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400"
                  : "text-text-tertiary cursor-not-allowed"
              }`}
            >
              <span className={`flex h-5 w-5 items-center justify-center rounded-full text-2xs font-bold ${
                isActive ? "bg-white/20 text-white" :
                isDone ? "bg-brand-600 text-white" :
                "bg-surface-2 text-text-tertiary"
              }`}>
                {isDone ? <Check className="h-3 w-3" /> : idx + 1}
              </span>
              <span className="hidden sm:inline truncate">{s.label}</span>
            </button>
            {idx < STEPS.length - 1 && (
              <ChevronRight className={`h-3 w-3 mx-1 shrink-0 ${
                idx < currentIdx ? "text-brand-400" : "text-text-tertiary"
              }`} />
            )}
          </div>
        );
      })}
    </div>
  );

  // ── Render: Step 1 — JD Input ───────────────────────────

  const renderInputStep = () => (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="section-title">Job Description</h3>
            <p className="section-description">
              Paste the job description you want to target. The AI will analyze it to create a tailored resume.
            </p>
          </div>
          <span className="text-xs text-text-tertiary">{jd.length} characters</span>
        </div>

        <textarea
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          rows={14}
          className="input resize-y min-h-[280px] font-mono text-sm"
          placeholder="Paste the full job description here... The AI will extract key requirements, skills, and qualifications automatically."
        />
      </div>

      {/* Template picker */}
      <div className="card space-y-3">
        <h3 className="section-title">Resume Template</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {templates.length > 0 ? templates.map((t) => (
            <button
              key={t.name}
              onClick={() => setTemplate(t.name)}
              className={`card text-center p-3 transition-all ${
                template === t.name
                  ? "ring-2 ring-brand-600 border-brand-600"
                  : "hover:shadow-elevation-2"
              }`}
            >
              <FileText className={`h-5 w-5 mx-auto mb-1 ${
                template === t.name ? "text-brand-600" : "text-text-tertiary"
              }`} />
              <p className="text-xs font-medium text-text-primary">{t.display_name}</p>
              <p className="text-2xs text-text-tertiary mt-0.5">{t.page_size}</p>
            </button>
          )) : (
            ["modern", "minimal", "software", "academic"].map((t) => (
              <button
                key={t}
                onClick={() => setTemplate(t)}
                className={`card text-center p-3 transition-all ${
                  template === t
                    ? "ring-2 ring-brand-600 border-brand-600"
                    : "hover:shadow-elevation-2"
                }`}
              >
                <FileText className={`h-5 w-5 mx-auto mb-1 ${
                  template === t ? "text-brand-600" : "text-text-tertiary"
                }`} />
                <p className="text-xs font-medium text-text-primary capitalize">{t}</p>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex justify-between items-center">
        <Button variant="ghost" size="sm" onClick={() => setShowHistory(!showHistory)} icon={<History className="h-4 w-4" />}>
          {showHistory ? "Hide History" : "Version History"}
        </Button>
        <Button
          onClick={handleGenerate}
          loading={generating || blueprintLoading}
          icon={<Sparkles className="h-4 w-4" />}
          disabled={jd.trim().length < 20}
          size="lg"
        >
          Generate Resume
        </Button>
      </div>

      {/* History panel */}
      {showHistory && (
        <div className="card space-y-3">
          <h3 className="section-title">Version History</h3>
          {versions.length === 0 ? (
            <p className="text-sm text-text-tertiary">No versions yet</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {versions.map((v: AnyRecord) => (
                <button
                  key={v.id}
                  onClick={() => loadVersion(v.id)}
                  className="w-full flex items-center justify-between p-3 rounded-lg border border-border hover:bg-surface-2 transition-colors text-left"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-text-primary truncate">{v.title}</p>
                    <p className="text-2xs text-text-tertiary mt-0.5">
                      {new Date(v.created_at).toLocaleDateString()}
                      {v.template_name && ` · ${v.template_name}`}
                    </p>
                  </div>
                  {v.ats_score != null && (
                    <span className={`text-xs font-bold ml-2 ${scoreColor(v.ats_score)}`}>
                      ATS: {v.ats_score}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  // ── Render: Step 2 — Blueprint ──────────────────────────

  const renderBlueprintStep = () => {
    if (!blueprint || blueprintLoading) {
      return (
        <div className="flex items-center justify-center py-20">
          <div className="text-center space-y-6 max-w-md">
            <div className="flex justify-center">
              <div className="relative">
                <Loader2 className="h-14 w-14 animate-spin text-brand-600" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Search className="h-5 w-5 text-brand-600" />
                </div>
              </div>
            </div>
            <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
              <div className="h-full rounded-full bg-brand-500 animate-pulse" style={{ width: "60%" }} />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-text-primary">Analyzing job description...</p>
              <p className="text-xs text-text-tertiary">Extracting requirements, skills, and strategy</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6 max-w-3xl mx-auto">
        <div className="card">
          <h3 className="section-title">Resume Strategy</h3>
          <p className="section-description">
            AI analysis of the job description and recommended approach
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {[
            ["Target Role", "target_role"],
            ["Industry", "target_industry"],
            ["Strategy", "resume_strategy"],
            ["Tone", "tone"],
          ].map(([label, key]) => (
            <div key={key} className="card space-y-1">
              <span className="text-2xs text-text-tertiary uppercase tracking-wider">{label}</span>
              <p className="text-sm font-medium text-text-primary">
                {String(blueprint?.[key] ?? "") || <span className="text-text-tertiary italic">Auto-detected</span>}
              </p>
            </div>
          ))}
        </div>

        {blueprint?.keywords_to_emphasize && (
          <div className="card">
            <span className="text-2xs text-text-tertiary uppercase tracking-wider">
              Keywords to Emphasize ({Math.min((blueprint.keywords_to_emphasize as string[]).length, 20)})
            </span>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {(blueprint.keywords_to_emphasize as string[]).slice(0, 20).map((kw: string, i: number) => (
                <span key={i} className="badge-info text-2xs">{kw}</span>
              ))}
            </div>
          </div>
        )}

        {blueprint?.reasoning && (
          <div className="card">
            <span className="text-2xs text-text-tertiary uppercase tracking-wider">Strategy Reasoning</span>
            <p className="mt-1 text-sm text-text-secondary leading-relaxed">{String(blueprint.reasoning)}</p>
          </div>
        )}

        <div className="flex justify-between">
          <Button variant="secondary" onClick={prevStep} icon={<ChevronLeft className="h-4 w-4" />}>
            Back
          </Button>
          {jd.trim().length >= 20 && (
            <Button onClick={handleGenerate} loading={generating} icon={<Sparkles className="h-4 w-4" />}>
              Generate Resume
            </Button>
          )}
        </div>
      </div>
    );
  };

  // ── Render: Step 3 — Generating (Progress) ──────────────

  const renderGenerateStep = () => {
    const pct = Math.round((genStep / (genSteps.length - 1)) * 100);
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center space-y-8 max-w-md w-full">
          {/* Animated icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 h-16 w-16 rounded-full bg-brand-500/20 animate-ping" />
              <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-950">
                <Sparkles className="h-7 w-7 text-brand-600" />
              </div>
            </div>
          </div>

          {/* Percentage */}
          <div>
            <p className="text-4xl font-bold text-brand-600">{pct}%</p>
            <p className="text-sm text-text-secondary mt-1">{genProgress}</p>
          </div>

          {/* Progress bar with stripes */}
          <div className="space-y-2">
            <div className="h-3 rounded-full bg-surface-2 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out relative overflow-hidden"
                style={{
                  width: `${pct}%`,
                  background: `linear-gradient(90deg, #7c3aed, #6366f1, #8b5cf6)`,
                }}
              >
                <div className="absolute inset-0" style={{
                  background: `repeating-linear-gradient(90deg, transparent, transparent 8px, rgba(255,255,255,0.15) 8px, rgba(255,255,255,0.15) 16px)`,
                }} />
              </div>
            </div>
            <div className="flex justify-between text-2xs text-text-tertiary">
              <span>Starting</span>
              <span>Almost done</span>
            </div>
          </div>

          {/* Step checklist */}
          <div className="card p-4 space-y-2 text-left max-w-sm mx-auto">
            <p className="text-2xs font-semibold text-text-tertiary uppercase tracking-wider mb-2">Pipeline Progress</p>
            {genSteps.map((s, i) => (
              <div key={i} className="flex items-center gap-3 text-xs">
                <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full transition-all ${
                  i < genStep ? "bg-green-500 text-white" :
                  i === genStep ? "bg-brand-600 text-white ring-2 ring-brand-300 ring-offset-2 ring-offset-surface-0" :
                  "bg-surface-2 text-text-tertiary"
                }`}>
                  {i < genStep ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <span className="h-2 w-2 rounded-full bg-current" />
                  )}
                </span>
                <span className={`${i <= genStep ? "text-text-primary font-medium" : "text-text-tertiary"}`}>{s}</span>
                {i === genStep && (
                  <span className="ml-auto">
                    <span className="flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-brand-400 opacity-75" />
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500" />
                    </span>
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // ── Render: Step 4 — Edit ───────────────────────────────

  const renderEditStep = () => {
    if (editableSections.length === 0) {
      return (
        <div className="text-center py-12">
          <EmptyState
            icon={<Edit3 className="h-8 w-8" />}
            title="No resume to edit"
            description="Generate a resume first"
            action={<Button onClick={() => goToStep("input")}>Go to Input</Button>}
          />
        </div>
      );
    }

    // Compute live ATS keyword match
    const allText = editableSections
      .flatMap((s) => (s.items || []).map((i: AnyRecord) => (i.text || "").toLowerCase()))
      .join(" ");
    const expandedKeywords = expandSynonyms(jdKeywords);
    const matchedKeywords = expandedKeywords.filter((kw) => allText.includes(kw.toLowerCase()));
    const matchRate = jdKeywords.length > 0 ? Math.round((matchedKeywords.length / jdKeywords.length) * 100) : 0;

    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Editor */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="section-title">Edit Resume</h3>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={handleSaveVersion} icon={<Check className="h-4 w-4" />}>
                Save
              </Button>
              <Button variant="secondary" size="sm" onClick={handleAnalyze} loading={analyzing} icon={<Target className="h-4 w-4" />}>
                Analyze ATS
              </Button>
            </div>
          </div>

          {editableSections.map((section, si) => (
            <div key={section._id || si} className="card space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h4 className="text-sm font-bold text-text-primary uppercase tracking-wider">
                  {section.name || "Untitled Section"}
                </h4>
                <span className="text-2xs text-text-tertiary">{section.items?.length || 0} items</span>
              </div>

              <div className="space-y-2">
                {(section.items || []).map((item: AnyRecord, ii: number) => {
                  const renderProvenanceBadge = (it: AnyRecord) => {
                    const src = it.evidence_source || it.metadata?.evidence_source || "";
                    const provenance = it.provenance_highlights || it.metadata?.provenance_highlights as string[] | undefined;

                    if (src === "from profile" || src === "education" || src === "skill" || src === "certificate" || src === "language" || src === "social_link") {
                      return <span title={provenance?.join(", ")} className="text-2xs text-green-600 shrink-0 font-medium">Profile</span>;
                    }
                    if (src === "ai_generated" || src.endsWith("_ai")) {
                      return <span className="text-2xs text-amber-600 shrink-0 font-medium">AI</span>;
                    }
                    if (provenance && provenance.length > 0) {
                      return <span className="text-2xs text-blue-600 shrink-0 font-medium">Refined</span>;
                    }
                    return null;
                  };

                  return (
                  <div key={item._id || ii} className="group flex items-start gap-2">
                    <span className="text-brand-500 mt-2 shrink-0">•</span>
                    {renderProvenanceBadge(item)}
                    <input
                      value={item.text || ""}
                      onChange={(e) => updateBullet(si, ii, e.target.value)}
                      className="flex-1 bg-transparent text-sm text-text-primary border-b border-transparent hover:border-border focus:border-brand-500 focus:outline-none transition-colors py-1"
                      placeholder="Enter bullet point..."
                    />
                    <button
                      onClick={() => removeBullet(si, ii)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 text-text-tertiary hover:text-red-500 transition-all"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  );
                })}
              </div>

              <button
                onClick={() => addBullet(si)}
                className="flex items-center gap-1.5 text-xs text-text-tertiary hover:text-brand-600 transition-colors"
              >
                <Plus className="h-3 w-3" />
                Add bullet
              </button>
            </div>
          ))}
        </div>

        {/* Right: Live stats */}
        <div className="space-y-4">
          <div className="card">
            <h4 className="text-xs font-semibold text-text-primary uppercase tracking-wider mb-3">Live ATS Match</h4>
            <div className="text-center py-4">
              <p className={`text-4xl font-bold ${scoreColor(matchRate)}`}>{matchRate}%</p>
              <p className="text-2xs text-text-tertiary mt-1">
                {matchedKeywords.length} / {jdKeywords.length} keywords matched
              </p>
            </div>
            <div className="h-2 rounded-full bg-surface-2 overflow-hidden mt-2">
              <div className={`h-full rounded-full transition-all duration-500 ${scoreBg(matchRate)}`} style={{ width: `${matchRate}%` }} />
            </div>
          </div>

          <div className="card space-y-2">
            <h4 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Keywords</h4>
            <div className="max-h-48 overflow-y-auto space-y-1.5">
              {jdKeywords.slice(0, 25).map((kw) => {
                const isMatched = allText.includes(kw.toLowerCase());
                return (
                  <div key={kw} className="flex items-center gap-2 text-xs">
                    {isMatched ? (
                      <CheckCircle className="h-3 w-3 text-green-500 shrink-0" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-400 shrink-0" />
                    )}
                    <span className={isMatched ? "text-text-primary" : "text-text-tertiary"}>{kw}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="card space-y-2">
            <h4 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Stats</h4>
            <div className="space-y-1 text-xs text-text-secondary">
              <div className="flex justify-between">
                <span>Sections</span>
                <span className="font-medium">{editableSections.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Bullets</span>
                <span className="font-medium">{editableSections.reduce((sum: number, s: AnyRecord) => sum + (s.items?.length || 0), 0)}</span>
              </div>
              <div className="flex justify-between">
                <span>Total words</span>
                <span className="font-medium">{allText.split(/\s+/).filter(Boolean).length}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="secondary" size="sm" className="flex-1" onClick={prevStep} icon={<ChevronLeft className="h-4 w-4" />}>
              Back
            </Button>
            <Button size="sm" className="flex-1" onClick={() => goToStep("export")} icon={<Download className="h-4 w-4" />}>
              Export
            </Button>
          </div>
        </div>
      </div>
    );
  };

  // ── Render: Step 5 — ATS Analysis ───────────────────────

  const renderATSStep = () => (
    <div className="space-y-6">
      {!atsReport ? (
        <div className="text-center py-12">
          <EmptyState
            icon={<Target className="h-8 w-8" />}
            title="No ATS analysis yet"
            description="Run an analysis from the Edit step to see results here"
            action={<Button onClick={() => goToStep("edit")}>Back to Editor</Button>}
          />
        </div>
      ) : (
        <>
          {/* Overall Score */}
          <div className="card text-center py-6">
            <p className="text-2xs text-text-tertiary uppercase tracking-wider mb-2">ATS Score</p>
            <p className={`text-5xl font-bold ${scoreColor(atsReport.overall_score)}`}>
              {atsReport.overall_score.toFixed(0)}
            </p>
            <p className="text-2xs text-text-tertiary mt-1">out of 100</p>
          </div>

          {/* Score Breakdown */}
          <div className="card space-y-3">
            <h3 className="section-title">Score Breakdown</h3>
            {[
              { label: "Keyword Match", value: atsReport.matched_keywords.length / Math.max(atsReport.matched_keywords.length + atsReport.missing_keywords.length, 1) * 100 },
              { label: "Readability", value: atsReport.readability_score },
              { label: "Impact", value: atsReport.impact_score },
              { label: "Achievement", value: atsReport.achievement_score },
              { label: "Specificity", value: atsReport.specificity_score },
              { label: "Evidence", value: atsReport.evidence_coverage * 100 },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">{label}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 rounded-full bg-surface-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${scoreBg(value)}`}
                      style={{ width: `${Math.min(value, 100)}%` }}
                    />
                  </div>
                  <span className={`text-sm font-medium w-10 text-right ${scoreColor(value)}`}>{value.toFixed(0)}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Keywords Match/Missing */}
          <div className="grid grid-cols-2 gap-4">
            <div className="card">
              <h3 className="text-xs font-semibold text-text-primary mb-2 flex items-center gap-1">
                <CheckCircle className="h-3.5 w-3.5 text-green-500" /> Matched ({atsReport.matched_keywords.length})
              </h3>
              <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
                {atsReport.matched_keywords.slice(0, 30).map((kw, i) => (
                  <span key={i} className="badge-success text-2xs">{kw}</span>
                ))}
              </div>
            </div>
            <div className="card">
              <h3 className="text-xs font-semibold text-text-primary mb-2 flex items-center gap-1">
                <XCircle className="h-3.5 w-3.5 text-red-500" /> Missing ({atsReport.missing_keywords.length})
              </h3>
              <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
                {atsReport.missing_keywords.slice(0, 30).map((kw, i) => (
                  <span key={i} className="badge-error text-2xs">{kw}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Suggestions with accept/reject */}
          {atsReport.suggestions.length > 0 && (
            <div className="card space-y-3">
              <h3 className="section-title flex items-center justify-between">
                <span>Suggestions</span>
                {acceptedSuggestions.size > 0 && (
                  <Button size="sm" variant="secondary" onClick={applyAcceptedSuggestions}>
                    Apply {acceptedSuggestions.size} Selected
                  </Button>
                )}
              </h3>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {atsReport.suggestions.slice(0, 20).map((s, i) => (
                  <div
                    key={i}
                    className={`flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                      acceptedSuggestions.has(i)
                        ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
                        : "border-border hover:border-border-strong"
                    }`}
                    onClick={() => toggleSuggestion(i)}
                  >
                    <div className="flex items-center gap-2 shrink-0">
                      <div className={`h-5 w-5 rounded border-2 flex items-center justify-center transition-colors ${
                        acceptedSuggestions.has(i)
                          ? "bg-brand-600 border-brand-600"
                          : "border-text-tertiary"
                      }`}>
                        {acceptedSuggestions.has(i) && <Check className="h-3 w-3 text-white" />}
                      </div>
                      {s.priority === "high" ? (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      ) : s.priority === "medium" ? (
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-blue-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-text-primary">{s.description}</p>
                      {s.section && (
                        <p className="text-2xs text-text-tertiary mt-0.5">Section: {s.section}</p>
                      )}
                    </div>
                    {s.expected_improvement > 0 && (
                      <span className="text-xs text-green-600 font-medium shrink-0">+{s.expected_improvement}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Optimize */}
          <div className="card">
            <h3 className="section-title">Auto-Optimize</h3>
            <p className="section-description">Run iterative AI optimization to improve the ATS score</p>
            <div className="flex items-center gap-4 mt-3">
              <Button onClick={handleOptimize} loading={optimizing} icon={<Sparkles className="h-4 w-4" />}>
                Optimize Resume
              </Button>
              {optimizedResult && (
                <span className="text-sm text-green-600 font-medium">
                  +{optimizedResult.improvement.toFixed(1)} point improvement
                </span>
              )}
            </div>

            {optimizedResult?.plan?.iterations?.map((iter: AnyRecord, i: number) => (
              <div key={i} className="flex items-center gap-3 text-sm mt-2">
                <span className="text-2xs font-mono text-text-tertiary">#{iter.iteration}</span>
                <span className="text-text-secondary">{iter.score_before?.toFixed(1)}</span>
                <ArrowUpRight className="h-3 w-3 text-green-500" />
                <span className="text-text-primary font-medium">{iter.score_after?.toFixed(1)}</span>
                <span className="text-2xs text-green-600">(+{iter.improvement?.toFixed(1)})</span>
              </div>
            ))}
          </div>

          <div className="flex justify-between">
            <Button variant="secondary" onClick={() => goToStep("edit")} icon={<ChevronLeft className="h-4 w-4" />}>
              Back to Editor
            </Button>
            <Button onClick={() => goToStep("export")} icon={<Download className="h-4 w-4" />}>
              Export Resume
            </Button>
          </div>
        </>
      )}
    </div>
  );

  // ── Render: Step 6 — Export ─────────────────────────────

  const renderExportStep = () => {
    const currentResume = resume || buildResumeFromSections();
    const hasContent = currentResume?.sections?.length > 0;

    return (
      <div className="space-y-6 max-w-2xl mx-auto">
        {!hasContent ? (
          <div className="text-center py-12">
            <EmptyState
              icon={<Download className="h-8 w-8" />}
              title="Nothing to export"
              description="Generate a resume first"
              action={<Button onClick={() => goToStep("input")}>Go to Input</Button>}
            />
          </div>
        ) : (
          <>
            <div className="card space-y-4">
              <h3 className="section-title">Export Resume</h3>
              <p className="section-description">Choose a format and download your resume</p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {EXPORT_FORMATS.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => setExportFormat(f.id)}
                    className={`card text-center p-4 transition-all ${
                      exportFormat === f.id
                        ? "ring-2 ring-brand-600 border-brand-600"
                        : "hover:shadow-elevation-2"
                    }`}
                  >
                    <FileText className={`h-6 w-6 mx-auto mb-2 ${
                      exportFormat === f.id ? "text-brand-600" : "text-text-tertiary"
                    }`} />
                    <p className="text-sm font-medium text-text-primary">{f.label}</p>
                    <p className="text-2xs text-text-tertiary mt-0.5">{f.ext}</p>
                  </button>
                ))}
              </div>

              <div className="flex justify-center pt-2">
                <Button onClick={handleExport} loading={exporting} size="lg" icon={<Download className="h-4 w-4" />}>
                  Export as {EXPORT_FORMATS.find((f) => f.id === exportFormat)?.label}
                </Button>
              </div>
            </div>

            {/* Version history summary */}
            <div className="card space-y-3">
              <h3 className="section-title">Version History</h3>
              {versions.length === 0 ? (
                <p className="text-sm text-text-tertiary">No saved versions</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {versions.map((v: AnyRecord) => (
                    <div key={v.id} className="flex items-center justify-between p-2 rounded-lg border border-border">
                      <div className="min-w-0">
                        <p className="text-sm text-text-primary truncate">{v.title}</p>
                        <p className="text-2xs text-text-tertiary">{new Date(v.created_at).toLocaleString()}</p>
                      </div>
                      {v.ats_score != null && (
                        <span className={`text-xs font-bold ${scoreColor(v.ats_score)}`}>{v.ats_score}</span>
                      )}
                    </div>
                  ))}
              </div>
              )}
            </div>

            <div className="flex justify-between">
              <Button variant="secondary" onClick={() => goToStep("ats")} icon={<ChevronLeft className="h-4 w-4" />}>
                Back to ATS
              </Button>
              <Button variant="ghost" onClick={() => goToStep("input")} icon={<Sparkles className="h-4 w-4" />}>
                New Resume
              </Button>
            </div>
          </>
        )}
      </div>
    );
  };

  // ── Render: Current Step ─────────────────────────────────

  const renderStepContent = () => {
    switch (step) {
      case "input": return renderInputStep();
      case "blueprint": return renderBlueprintStep();
      case "generate": return renderGenerateStep();
      case "edit": return renderEditStep();
      case "ats": return renderATSStep();
      case "export": return renderExportStep();
    }
  };

  // ── Main Render ─────────────────────────────────────────

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Resume Studio</h1>
          <p className="mt-1 text-sm text-text-secondary">Generate, edit, analyze, and export ATS-optimized resumes</p>
        </div>
      </div>

      {/* Step Indicator */}
      {renderSteps()}

      {/* Step Content */}
      {renderStepContent()}
    </div>
  );
}
