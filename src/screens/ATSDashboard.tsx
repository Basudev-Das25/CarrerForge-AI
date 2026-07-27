import { useEffect, useState } from "react";
import {
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Search,
  BarChart3,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyRecord = Record<string, any>;

interface ATSReport {
  overall_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  keyword_density: number;
  semantic_score: number;
  skill_similarity: number;
  experience_relevance: number;
  industry_alignment: number;
  readability_score: number;
  impact_score: number;
  achievement_score: number;
  specificity_score: number;
  evidence_coverage: number;
  unsupported_claims: number;
  suggestions: Array<{ priority: string; description: string; section: string; expected_improvement: number }>;
  sections: Array<{ name: string; score: number; suggestions: string[] }>;
  missing_sections: string[];
}

export default function ATSDashboard() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [report, setReport] = useState<ATSReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizedResult, setOptimizedResult] = useState<AnyRecord | null>(null);
  const [activeTab, setActiveTab] = useState<"analyze" | "optimize" | "comparison" | "history">("analyze");
  const [reports, setReports] = useState<Array<{ id: string; score: number; created_at: string }>>([]);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const d = await api.listAtsReports();
      setReports(d.reports || []);
    } catch {}
  };

  const handleAnalyze = async () => {
    if (!resumeText.trim() || !jobText.trim()) { toast.error("Paste both resume and job description"); return; }
    setAnalyzing(true);
    try {
      const resume = { sections: [{ name: "Full Resume", items: [{ text: resumeText }] }] };

      // Smarter keyword extraction from JD
      const jdLower = jobText.toLowerCase();
      const words = jdLower.split(/[\s,;()\[\]{}]+/);
      const stopWords = new Set(["the", "and", "for", "with", "this", "that", "from", "will", "have", "are", "was", "were", "been", "being", "can", "may", "our", "your", "their", "its", "who", "what", "which", "where", "when", "how", "all", "each", "than", "them", "then", "also", "such", "into", "over", "only", "very", "not", "but", "about", "more", "other", "some", "any", "most", "just", "should", "would", "could"]);
      const keywords = [...new Set(words.filter((w) => w.length > 2 && !stopWords.has(w)))].slice(0, 40);

      // Extract tech/skill mentions
      const techPatterns = ["python", "javascript", "typescript", "react", "node", "java", "c\\+\\+", "rust", "go", "ruby", "php", "swift", "kotlin", "sql", "nosql", "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "machine learning", "deep learning", "ai", "nlp", "html", "css", "sass", "tailwind", "fastapi", "django", "flask", "express", "nextjs", "vue", "angular", "svelte", "postgresql", "mysql", "mongodb", "redis", "graphql", "rest", "api", "microservices", "ci/cd", "terraform", "jenkins"];
      const technologies = techPatterns.filter((t) => jdLower.includes(t));

      const jobProfile: Record<string, string | string[]> = {
        keywords,
        ats_keywords: keywords.slice(0, 20),
        required_skills: technologies,
        technologies,
        summary: jobText.slice(0, 2000),
        raw_jd: jobText,
      };

      const d = await api.analyzeResume(resume, jobProfile);
      setReport(d.report as unknown as ATSReport);
      setActiveTab("analyze");
    } catch {
      toast.error("Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleOptimize = async () => {
    if (!report) { toast.error("Run analysis first"); return; }
    setOptimizing(true);
    try {
      const resume = { sections: [{ name: "Full Resume", items: [{ text: resumeText }] }] };
      const jobProfile = {
        keywords: report.matched_keywords,
        ats_keywords: report.missing_keywords,
        required_skills: [],
        technologies: [],
        summary: jobText.slice(0, 2000),
        raw_jd: jobText,
      };
      const d = await api.optimizeResume(resume, jobProfile, 85, 3);
      setOptimizedResult(d);
      toast.success(`Score improved from ${d.initial_score.toFixed(1)} to ${d.final_score.toFixed(1)}`);
    } catch {
      toast.error("Optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-amber-600";
    return "text-red-600";
  };

  const renderScoreGauge = (label: string, score: number, icon: React.ReactNode) => (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {icon}
        <span className="text-sm text-text-secondary">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-24 h-2 rounded-full bg-surface-2 overflow-hidden">
          <div className={`h-full rounded-full transition-all duration-500 ${score >= 80 ? "bg-green-500" : score >= 60 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${Math.min(score, 100)}%` }} />
        </div>
        <span className={`text-sm font-medium w-12 text-right ${scoreColor(score)}`}>{score.toFixed(0)}</span>
      </div>
    </div>
  );

  const renderAnalysisTab = () => {
    if (!report) return <EmptyState icon={<Target className="h-8 w-8" />} title="No analysis yet" description="Paste resume and job description, then click Analyze" />;
    return (
      <div className="space-y-6">
        {/* Overall Score */}
        <div className="card text-center py-6">
          <p className="text-sm text-text-secondary uppercase tracking-wider mb-2">ATS Score</p>
          <p className={`text-5xl font-bold ${scoreColor(report.overall_score)}`}>{report.overall_score.toFixed(0)}</p>
          <p className="text-xs text-text-tertiary mt-1">out of 100</p>
        </div>

        {/* Category Scores */}
        <div className="card space-y-3">
          <h3 className="section-title">Score Breakdown</h3>
          {renderScoreGauge("Keyword Match", (report.matched_keywords.length / Math.max(report.matched_keywords.length + report.missing_keywords.length, 1)) * 100, <Target className="h-4 w-4 text-brand-500" />)}
          {renderScoreGauge("Readability", report.readability_score, <BarChart3 className="h-4 w-4 text-blue-500" />)}
          {renderScoreGauge("Impact", report.impact_score, <TrendingUp className="h-4 w-4 text-green-500" />)}
          {renderScoreGauge("Achievement", report.achievement_score, <CheckCircle className="h-4 w-4 text-purple-500" />)}
          {renderScoreGauge("Specificity", report.specificity_score, <Target className="h-4 w-4 text-amber-500" />)}
          {renderScoreGauge("Semantic", report.semantic_score, <Search className="h-4 w-4 text-cyan-500" />)}
          {renderScoreGauge("Evidence", report.evidence_coverage * 100, <CheckCircle className="h-4 w-4 text-emerald-500" />)}
        </div>

        {/* Keywords */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card">
            <h3 className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" /> Matched ({report.matched_keywords.length})
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {report.matched_keywords.slice(0, 20).map((kw, i) => (
                <span key={i} className="badge-success text-2xs">{kw}</span>
              ))}
            </div>
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" /> Missing ({report.missing_keywords.length})
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {report.missing_keywords.slice(0, 20).map((kw, i) => (
                <span key={i} className="badge-error text-2xs">{kw}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Suggestions */}
        {report.suggestions.length > 0 && (
          <div className="card space-y-3">
            <h3 className="section-title">Suggestions</h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {report.suggestions.slice(0, 15).map((s, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-border">
                  {s.priority === "high" ? <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                    : s.priority === "medium" ? <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                    : <AlertTriangle className="h-4 w-4 text-blue-400 mt-0.5 shrink-0" />}
                  <div>
                    <p className="text-sm text-text-primary">{s.description}</p>
                    {s.section && <p className="text-2xs text-text-tertiary mt-0.5">Section: {s.section}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderOptimizeTab = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="section-title">Auto-Optimize</h3>
        <p className="section-description">Run iterative optimization to improve ATS score</p>
        <div className="mt-4">
          <Button onClick={handleOptimize} loading={optimizing} icon={<Sparkles className="h-4 w-4" />}>
            Optimize Resume
          </Button>
        </div>
      </div>
      {optimizedResult && (
        <div className="card space-y-4">
          <h3 className="section-title">Optimization Results</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-text-secondary">Before</p>
              <p className={`text-2xl font-bold ${scoreColor(optimizedResult.initial_score)}`}>{optimizedResult.initial_score.toFixed(0)}</p>
            </div>
            <div className="flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-green-500" />
              <span className="ml-1 text-green-600 font-medium">+{optimizedResult.improvement.toFixed(1)}</span>
            </div>
            <div>
              <p className="text-sm text-text-secondary">After</p>
              <p className={`text-2xl font-bold ${scoreColor(optimizedResult.final_score)}`}>{optimizedResult.final_score.toFixed(0)}</p>
            </div>
          </div>
          {/* Iteration log */}
          {optimizedResult.plan?.iterations?.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-text-primary mb-2">Iteration Log</h4>
              <div className="space-y-2">
                {(optimizedResult.plan.iterations as AnyRecord[]).map((iter: AnyRecord, i: number) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <span className="text-xs font-mono text-text-tertiary">#{iter.iteration}</span>
                    <span className="text-text-secondary">{iter.score_before.toFixed(1)}</span>
                    <ArrowUpRight className="h-3 w-3 text-green-500" />
                    <span className="text-text-primary font-medium">{iter.score_after.toFixed(1)}</span>
                    <span className="text-2xs text-green-600">(+{iter.improvement.toFixed(1)})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderHistoryTab = () => {
    if (reports.length === 0) return <EmptyState icon={<BarChart3 className="h-8 w-8" />} title="No ATS reports" description="Run an analysis to see history" />;
    return (
      <div className="space-y-3 max-w-2xl">
        {reports.map((r) => (
          <div key={r.id} className="card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-text-primary">Report {r.id.slice(0, 8)}</p>
                <p className="text-xs text-text-tertiary">{new Date(r.created_at).toLocaleString()}</p>
              </div>
              <span className={`badge ${r.score >= 80 ? "badge-success" : r.score >= 60 ? "badge-warning" : "badge-error"}`}>
                Score: {r.score.toFixed(0)}
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">ATS Intelligence</h1>
        <p className="mt-1 text-sm text-text-secondary">Analyze, optimize, and score your resume against job descriptions</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {[
          { key: "analyze", label: "Analyze", icon: Target },
          { key: "optimize", label: "Optimize", icon: Sparkles },
          { key: "history", label: "History", icon: BarChart3 },
        ].map((tab) => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key as typeof activeTab)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.key ? "bg-surface-1 text-brand-600 border-b-2 border-brand-600" : "text-text-secondary hover:text-text-primary"
            }`}>
            <tab.icon className="h-4 w-4" /> {tab.label}
          </button>
        ))}
      </div>

      {/* Input */}
      {activeTab === "analyze" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card space-y-4">
            <h3 className="section-title">Resume Content</h3>
            <textarea value={resumeText} onChange={(e) => setResumeText(e.target.value)}
              rows={8} className="input resize-y min-h-[160px] text-sm" placeholder="Paste your resume content here..." />
          </div>
          <div className="card space-y-4">
            <h3 className="section-title">Job Description</h3>
            <textarea value={jobText} onChange={(e) => setJobText(e.target.value)}
              rows={8} className="input resize-y min-h-[160px] text-sm" placeholder="Paste the job description here..." />
          </div>
          <div className="lg:col-span-2 flex justify-center">
            <Button onClick={handleAnalyze} loading={analyzing} size="lg" icon={<Target className="h-4 w-4" />}>
              Analyze Resume
            </Button>
          </div>
          <div className="lg:col-span-2">{renderAnalysisTab()}</div>
        </div>
      )}

      {activeTab === "optimize" && renderOptimizeTab()}
      {activeTab === "history" && renderHistoryTab()}
    </div>
  );
}
