/**
 * Settings — Full application settings screen with tabbed sections.
 *
 * Tabs:
 *   General  – Theme, sidebar, animations
 *   AI       – Provider, API key, model
 *   Resume   – Default template, ATS threshold, iterations
 *   Security – Encryption, backup, auto-lock
 *   About    – Version, links, diagnostics
 */

import { useEffect, useState, useCallback } from "react";
import {
  Palette,
  Bot,
  FileText,
  Shield,
  Info,
  Save,
  Eye,
  EyeOff,
  Monitor,
  Sun,
  Moon,
  ChevronDown,
  ChevronUp,
  Download,
  ExternalLink,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { useAppStore } from "@/hooks/useStore";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { toast } from "@/components/common/Toast";
import type { ProviderID } from "@/types";

/* eslint-disable @typescript-eslint/no-explicit-any */

// ── Constants ─────────────────────────────────────────────────

type SettingsTab = "general" | "ai" | "resume" | "security" | "about";

const TABS: { key: SettingsTab; label: string; icon: typeof Palette }[] = [
  { key: "general", label: "General", icon: Palette },
  { key: "ai", label: "AI", icon: Bot },
  { key: "resume", label: "Resume", icon: FileText },
  { key: "security", label: "Security", icon: Shield },
  { key: "about", label: "About", icon: Info },
];

const PROVIDERS: { id: ProviderID; name: string; desc: string; needsKey: boolean; placeholder: string }[] = [
  { id: "openai", name: "OpenAI", desc: "GPT-4o, GPT-4o-mini", needsKey: true, placeholder: "sk-..." },
  { id: "claude", name: "Claude", desc: "Sonnet, Haiku, Opus", needsKey: true, placeholder: "sk-ant-..." },
  { id: "openrouter", name: "OpenRouter", desc: "Multi-model gateway", needsKey: true, placeholder: "sk-or-v1-..." },
  { id: "grok", name: "Grok", desc: "xAI models", needsKey: true, placeholder: "xai-..." },
  { id: "huggingface", name: "HuggingFace", desc: "Free tier available", needsKey: true, placeholder: "hf_..." },
  { id: "ollama", name: "Ollama", desc: "Local models (no key)", needsKey: false, placeholder: "" },
];

const TEMPLATES = [
  { id: "modern", name: "Modern", desc: "Clean, professional" },
  { id: "minimal", name: "Minimal", desc: "Content-forward" },
  { id: "software", name: "Software", desc: "Technical grid" },
  { id: "academic", name: "Academic", desc: "Formal CV" },
];

// ── Helpers ───────────────────────────────────────────────────

function listenForThemeChanges(theme: string) {
  if (theme !== "system") return;
  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  const handler = () => {
    document.documentElement.classList.toggle("dark", mq.matches);
  };
  mq.addEventListener("change", handler);
  return () => mq.removeEventListener("change", handler);
}

// ── Component ─────────────────────────────────────────────────

export default function Settings() {
  const navigate = useNavigate();

  // ── Store bindings ────────────────────────────────────────
  const storeTheme = useAppStore((s) => s.theme);
  const setStoreTheme = useAppStore((s) => s.setTheme);
  const activeProvider = useAppStore((s) => s.activeProvider);
  const setActiveProvider = useAppStore((s) => s.setActiveProvider);
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);

  // ── Tab state ─────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");

  // ── AI settings ───────────────────────────────────────────
  const [aiApiKey, setAiApiKey] = useState("");
  const [aiModel, setAiModel] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [savingAi, setSavingAi] = useState(false);
  const [aiSettingsOpen, setAiSettingsOpen] = useState(false);

  // ── Resume defaults ───────────────────────────────────────
  const [defaultTemplate, setDefaultTemplate] = useState("modern");
  const [atsThreshold, setAtsThreshold] = useState(80);
  const [maxIterations, setMaxIterations] = useState(3);

  // ── Security settings ─────────────────────────────────────
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [autoLockMinutes, setAutoLockMinutes] = useState(5);
  const [backupEnabled, setBackupEnabled] = useState(true);

  // ── UI settings ───────────────────────────────────────────
  const [animationsEnabled, setAnimationsEnabled] = useState(true);

  // ── About / Version ───────────────────────────────────────
  const [appVersion, setAppVersion] = useState("0.1.0");
  const [exportingDiag, setExportingDiag] = useState(false);

  // ── Saving state for each section ─────────────────────────
  const [savingResume, setSavingResume] = useState(false);
  const [savingSecurity, setSavingSecurity] = useState(false);

  // ── Load settings on mount ────────────────────────────────
  useEffect(() => {
    loadAiConfig();
    loadResumeDefaults();
    loadVersion();
    loadUiSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Track system theme changes
  useEffect(() => {
    const cleanup = listenForThemeChanges(storeTheme);
    return cleanup;
  }, [storeTheme]);

  // ── Data loaders ──────────────────────────────────────────

  const loadAiConfig = async () => {
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/v1/config/ai");
      if (resp.ok) {
        const cfg = await resp.json();
        if (cfg.ai_provider) setActiveProvider(cfg.ai_provider);
        if (cfg.model) setAiModel(cfg.model);
        const savedKey = localStorage.getItem(`careerforge_provider_${cfg.ai_provider || activeProvider}`);
        if (savedKey) setAiApiKey(savedKey);
      }
    } catch { /* backend not ready */ }
  };

  const loadResumeDefaults = async () => {
    try {
      const d = await api.listResumeTemplates();
      if (d.templates?.length > 0) setDefaultTemplate(d.templates[0].name);
    } catch { /* ignore */ }
    // Backend config doesn't expose template/iteration settings yet,
    // so load from localStorage fallback
    const savedTemplate = localStorage.getItem("careerforge_default_template");
    if (savedTemplate) setDefaultTemplate(savedTemplate);
    const savedThreshold = localStorage.getItem("careerforge_ats_threshold");
    if (savedThreshold) setAtsThreshold(Number(savedThreshold));
    const savedIterations = localStorage.getItem("careerforge_max_iterations");
    if (savedIterations) setMaxIterations(Number(savedIterations));
  };

  const loadVersion = async () => {
    try {
      const d = await api.getCurrentVersion();
      setAppVersion(d.version);
    } catch { /* use default */ }
  };

  const loadUiSettings = () => {
    const stored = localStorage.getItem("careerforge_ui_settings");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (typeof parsed.animationsEnabled === "boolean") setAnimationsEnabled(parsed.animationsEnabled);
      } catch { /* ignore */ }
    }
  };

  // ── Persistence helpers ───────────────────────────────────

  const persistUiSettings = useCallback((updates: Record<string, any>) => {
    const current = { animationsEnabled, ...updates };
    localStorage.setItem("careerforge_ui_settings", JSON.stringify(current));
  }, [animationsEnabled]);

  // ── AI config save ────────────────────────────────────────

  const handleSaveAi = async () => {
    setSavingAi(true);
    try {
      const providerDef = PROVIDERS.find((p) => p.id === activeProvider);
      if (!providerDef) { toast.error("Select a provider"); return; }

      const payload: Record<string, string> = { ai_provider: activeProvider };
      if (providerDef.needsKey && aiApiKey) {
        const keyField = `${activeProvider}_api_key`;
        payload[keyField] = aiApiKey;
        localStorage.setItem(`careerforge_provider_${activeProvider}`, aiApiKey);
      }
      if (aiModel) {
        payload.model = aiModel;
        localStorage.setItem(`careerforge_model_${activeProvider}`, aiModel);
      }

      const resp = await fetch("http://127.0.0.1:8000/api/v1/config/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        toast.success(`AI provider set to ${providerDef.name}`);
      } else {
        const err = await resp.json().catch(() => ({ detail: "Save failed" }));
        toast.error(err.detail || "Failed to save AI config");
      }
    } catch {
      toast.error("Could not reach backend");
    } finally {
      setSavingAi(false);
    }
  };

  // ── Resume defaults save ──────────────────────────────────

  const handleSaveResume = async () => {
    setSavingResume(true);
    try {
      // Persist template and defaults to localStorage for now
      localStorage.setItem("careerforge_default_template", defaultTemplate);
      localStorage.setItem("careerforge_ats_threshold", String(atsThreshold));
      localStorage.setItem("careerforge_max_iterations", String(maxIterations));
      toast.success("Resume defaults saved");
    } catch {
      toast.error("Failed to save resume defaults");
    } finally {
      setSavingResume(false);
    }
  };

  // ── Security settings save ────────────────────────────────

  const handleSaveSecurity = async () => {
    setSavingSecurity(true);
    try {
      localStorage.setItem("careerforge_encryption", String(encryptionEnabled));
      localStorage.setItem("careerforge_auto_lock", String(autoLockMinutes));
      localStorage.setItem("careerforge_backup", String(backupEnabled));
      toast.success("Security settings saved");
    } catch {
      toast.error("Failed to save security settings");
    } finally {
      setSavingSecurity(false);
    }
  };

  // ── Diagnostics export ────────────────────────────────────

  const handleExportDiag = async () => {
    setExportingDiag(true);
    try {
      const d = await api.exportDiagnostics();
      toast.success(`Diagnostics exported to ${(d as any).path}`);
    } catch {
      toast.error("Export failed");
    } finally {
      setExportingDiag(false);
    }
  };

  // ── Reset all settings ────────────────────────────────────

  const handleResetAll = () => {
    if (!confirm("Reset all settings to defaults? This cannot be undone.")) return;
    localStorage.removeItem("careerforge_ui_settings");
    localStorage.removeItem("careerforge_default_template");
    localStorage.removeItem("careerforge_ats_threshold");
    localStorage.removeItem("careerforge_max_iterations");
    localStorage.removeItem("careerforge_encryption");
    localStorage.removeItem("careerforge_auto_lock");
    localStorage.removeItem("careerforge_backup");
    setStoreTheme("system");
    setActiveProvider("openai");
    setAnimationsEnabled(true);
    setDefaultTemplate("modern");
    setAtsThreshold(80);
    setMaxIterations(3);
    setEncryptionEnabled(true);
    setAutoLockMinutes(5);
    setBackupEnabled(true);
    toast.success("Settings reset to defaults");
  };

  // ── Theme helpers ─────────────────────────────────────────

  const handleThemeChange = (theme: "light" | "dark" | "system") => {
    setStoreTheme(theme);
  };

  // ── Toggle helpers ────────────────────────────────────────

  const handleAnimationsToggle = () => {
    const next = !animationsEnabled;
    setAnimationsEnabled(next);
    persistUiSettings({ animationsEnabled: next });
  };

  // ── Render: General Tab ───────────────────────────────────

  const renderGeneral = () => (
    <div className="space-y-6">
      {/* Theme */}
      <div className="card space-y-4">
        <h3 className="section-title">Theme</h3>
        <p className="section-description">Choose how CareerForge AI looks</p>
        <div className="grid grid-cols-3 gap-3">
          {[
            { value: "light" as const, label: "Light", icon: Sun, desc: "Always light" },
            { value: "dark" as const, label: "Dark", icon: Moon, desc: "Always dark" },
            { value: "system" as const, label: "System", icon: Monitor, desc: "Follow OS" },
          ].map(({ value, label, icon: Icon, desc }) => (
            <button
              key={value}
              onClick={() => handleThemeChange(value)}
              className={`card text-center p-4 transition-all ${
                storeTheme === value
                  ? "ring-2 ring-brand-600 border-brand-600"
                  : "hover:shadow-elevation-2"
              }`}
            >
              <Icon className={`h-6 w-6 mx-auto mb-2 ${
                storeTheme === value ? "text-brand-600" : "text-text-tertiary"
              }`} />
              <p className="text-sm font-medium text-text-primary">{label}</p>
              <p className="text-2xs text-text-tertiary mt-0.5">{desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Sidebar */}
      <div className="card space-y-4">
        <h3 className="section-title">Sidebar</h3>
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm font-medium text-text-primary">Collapse sidebar by default</p>
            <p className="text-xs text-text-tertiary mt-0.5">More room for content</p>
          </div>
          <button
            onClick={toggleSidebar}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              sidebarCollapsed ? "bg-brand-600" : "bg-surface-3"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                sidebarCollapsed ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </label>
      </div>

      {/* Animations */}
      <div className="card space-y-4">
        <h3 className="section-title">Animations</h3>
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm font-medium text-text-primary">Enable animations</p>
            <p className="text-xs text-text-tertiary mt-0.5">Page transitions and effects</p>
          </div>
          <button
            onClick={handleAnimationsToggle}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              animationsEnabled ? "bg-brand-600" : "bg-surface-3"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                animationsEnabled ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </label>
      </div>
    </div>
  );

  // ── Render: AI Tab ────────────────────────────────────────

  const renderAi = () => (
    <div className="space-y-6">
      <div className="card space-y-4">
        <h3 className="section-title">AI Provider</h3>
        <p className="section-description">
          Select the AI service used for resume generation and ATS analysis
        </p>

        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              onClick={() => { setActiveProvider(p.id); setAiApiKey(""); }}
              className={`card text-left p-3 transition-all ${
                activeProvider === p.id
                  ? "ring-2 ring-brand-600 border-brand-600"
                  : "hover:shadow-elevation-2"
              }`}
            >
              <p className="font-semibold text-text-primary text-sm">{p.name}</p>
              <p className="text-2xs text-text-tertiary mt-1">{p.desc}</p>
              {p.needsKey ? (
                <span className="badge badge-info text-2xs mt-1.5 inline-block">API key required</span>
              ) : (
                <span className="badge badge-success text-2xs mt-1.5 inline-block">No key needed</span>
              )}
            </button>
          ))}
        </div>

        {PROVIDERS.find((p) => p.id === activeProvider)?.needsKey && (
          <div className="space-y-3 pt-2">
            <Input
              label="API Key"
              type={showKey ? "text" : "password"}
              value={aiApiKey}
              onChange={(e) => setAiApiKey(e.target.value)}
              placeholder={PROVIDERS.find((p) => p.id === activeProvider)?.placeholder || ""}
              icon={
                <button
                  tabIndex={-1}
                  onClick={() => setShowKey(!showKey)}
                  className="text-text-tertiary hover:text-text-primary"
                >
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
            />
          </div>
        )}

        <div className="pt-2">
          <button
            onClick={() => setAiSettingsOpen(!aiSettingsOpen)}
            className="flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary"
          >
            <Bot className="h-4 w-4" />
            Advanced model settings
            {aiSettingsOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
          {aiSettingsOpen && (
            <div className="mt-3 space-y-3 border-t border-border pt-3">
              <Input
                label="Model"
                value={aiModel}
                onChange={(e) => setAiModel(e.target.value)}
                placeholder={PROVIDERS.find((p) => p.id === activeProvider)?.id === "openai" ? "gpt-4o" : "default model"}
                hint="Leave blank to use provider default"
              />
            </div>
          )}
        </div>

        <div className="flex justify-end pt-2">
          <Button onClick={handleSaveAi} loading={savingAi} icon={<Save className="h-4 w-4" />}>
            Save Provider Settings
          </Button>
        </div>
      </div>
    </div>
  );

  // ── Render: Resume Tab ────────────────────────────────────

  const renderResume = () => (
    <div className="space-y-6">
      {/* Default Template */}
      <div className="card space-y-4">
        <h3 className="section-title">Default Template</h3>
        <p className="section-description">Template used when generating new resumes</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {TEMPLATES.map((t) => (
            <button
              key={t.id}
              onClick={() => setDefaultTemplate(t.id)}
              className={`card text-center p-4 transition-all ${
                defaultTemplate === t.id
                  ? "ring-2 ring-brand-600 border-brand-600"
                  : "hover:shadow-elevation-2"
              }`}
            >
              <FileText className={`h-6 w-6 mx-auto mb-2 ${
                defaultTemplate === t.id ? "text-brand-600" : "text-text-tertiary"
              }`} />
              <p className="text-sm font-medium text-text-primary capitalize">{t.name}</p>
              <p className="text-2xs text-text-tertiary mt-0.5">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* ATS Threshold */}
      <div className="card space-y-4">
        <h3 className="section-title">ATS Score Threshold</h3>
        <p className="section-description">Minimum ATS score target when optimizing resumes</p>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={atsThreshold}
            onChange={(e) => setAtsThreshold(Number(e.target.value))}
            className="flex-1 h-2 rounded-full appearance-none cursor-pointer bg-surface-2 accent-brand-600"
          />
          <span className="text-lg font-bold text-text-primary w-10 text-right">{atsThreshold}</span>
        </div>
        <div className="flex justify-between text-2xs text-text-tertiary">
          <span>0 (Minimum)</span>
          <span>100 (Maximum)</span>
        </div>
      </div>

      {/* Max Iterations */}
      <div className="card space-y-4">
        <h3 className="section-title">Refinement Iterations</h3>
        <p className="section-description">Number of AI refinement passes during resume generation</p>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min={1}
            max={10}
            value={maxIterations}
            onChange={(e) => setMaxIterations(Number(e.target.value))}
            className="flex-1 h-2 rounded-full appearance-none cursor-pointer bg-surface-2 accent-brand-600"
          />
          <span className="text-lg font-bold text-text-primary w-6 text-right">{maxIterations}</span>
        </div>
        <div className="flex justify-between text-2xs text-text-tertiary">
          <span>1 (Fast)</span>
          <span>10 (Thorough)</span>
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSaveResume} loading={savingResume} icon={<Save className="h-4 w-4" />}>
          Save Resume Defaults
        </Button>
      </div>
    </div>
  );

  // ── Render: Security Tab ──────────────────────────────────

  const renderSecurity = () => (
    <div className="space-y-6">
      <div className="card space-y-4">
        <h3 className="section-title">Encryption</h3>
        <p className="section-description">Protect your data at rest</p>
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm font-medium text-text-primary">Encrypt local data</p>
            <p className="text-xs text-text-tertiary mt-0.5">Uses system keychain for encryption keys</p>
          </div>
          <button
            onClick={() => setEncryptionEnabled(!encryptionEnabled)}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              encryptionEnabled ? "bg-brand-600" : "bg-surface-3"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                encryptionEnabled ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </label>
      </div>

      <div className="card space-y-4">
        <h3 className="section-title">Auto-Lock</h3>
        <p className="section-description">Automatically lock the app after inactivity</p>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min={0}
            max={60}
            step={5}
            value={autoLockMinutes}
            onChange={(e) => setAutoLockMinutes(Number(e.target.value))}
            className="flex-1 h-2 rounded-full appearance-none cursor-pointer bg-surface-2 accent-brand-600"
          />
          <span className="text-sm font-bold text-text-primary w-16 text-right">
            {autoLockMinutes === 0 ? "Off" : `${autoLockMinutes}m`}
          </span>
        </div>
        <div className="flex justify-between text-2xs text-text-tertiary">
          <span>Off</span>
          <span>60 min</span>
        </div>
      </div>

      <div className="card space-y-4">
        <h3 className="section-title">Backup</h3>
        <p className="section-description">Automatically back up your data</p>
        <label className="flex items-center justify-between cursor-pointer">
          <div>
            <p className="text-sm font-medium text-text-primary">Enable periodic backups</p>
            <p className="text-xs text-text-tertiary mt-0.5">Backups stored in your data directory</p>
          </div>
          <button
            onClick={() => setBackupEnabled(!backupEnabled)}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              backupEnabled ? "bg-brand-600" : "bg-surface-3"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                backupEnabled ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </label>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSaveSecurity} loading={savingSecurity} icon={<Save className="h-4 w-4" />}>
          Save Security Settings
        </Button>
      </div>
    </div>
  );

  // ── Render: About Tab ─────────────────────────────────────

  const renderAbout = () => (
    <div className="space-y-6 max-w-2xl">
      {/* App Info */}
      <div className="card text-center py-6 space-y-4">
        <div className="flex justify-center">
          <div className="h-16 w-16 rounded-2xl bg-brand-600 flex items-center justify-center shadow-lg">
            <span className="text-white text-2xl font-bold">CF</span>
          </div>
        </div>
        <div>
          <h2 className="text-xl font-bold text-text-primary">CareerForge AI</h2>
          <p className="text-sm text-text-tertiary mt-1">Version {appVersion}</p>
        </div>
        <p className="text-sm text-text-secondary max-w-md mx-auto">
          AI-powered desktop career intelligence platform for resume generation,
          ATS optimization, document management, and career development.
        </p>
      </div>

      {/* Links */}
      <div className="card space-y-3">
        <h3 className="section-title">Resources</h3>
        <div className="space-y-2">
          {[
            { label: "GitHub Repository", url: "https://github.com/Basudev-Das/CareerForge-AI" },
            { label: "Documentation", url: "https://github.com/Basudev-Das/CareerForge-AI/tree/main/docs" },
            { label: "Report a Bug", url: "https://github.com/Basudev-Das/CareerForge-AI/issues/new" },
            { label: "Request a Feature", url: "https://github.com/Basudev-Das/CareerForge-AI/issues/new?template=feature_request.md" },
          ].map((link) => (
            <a
              key={link.label}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-surface-2 transition-colors"
            >
              <span className="text-sm text-text-primary">{link.label}</span>
              <ExternalLink className="h-3.5 w-3.5 text-text-tertiary" />
            </a>
          ))}
        </div>
      </div>

      {/* Third-Party Libraries */}
      <div className="card space-y-3">
        <h3 className="section-title">Third-Party Libraries</h3>
        <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary">
          <span>React 19</span><span>FastAPI</span>
          <span>SQLAlchemy 2.0</span><span>LanceDB</span>
          <span>Tauri 2</span><span>Typst</span>
          <span>Zustand 5</span><span>Pydantic 2</span>
          <span>Tailwind CSS</span><span>structlog</span>
        </div>
      </div>

      {/* License */}
      <div className="card space-y-3">
        <h3 className="section-title">License</h3>
        <p className="text-sm text-text-secondary">CareerForge AI — All rights reserved.</p>
      </div>

      {/* Diagnostics */}
      <div className="card space-y-4">
        <h3 className="section-title">Diagnostics</h3>
        <p className="section-description">
          Export diagnostic information to help troubleshoot issues. API keys are automatically redacted.
        </p>
        <Button onClick={handleExportDiag} loading={exportingDiag} variant="secondary" icon={<Download className="h-4 w-4" />}>
          Export Diagnostics
        </Button>
      </div>
    </div>
  );

  // ── Render: Tab Switcher ──────────────────────────────────

  const renderTabContent = () => {
    switch (activeTab) {
      case "general": return renderGeneral();
      case "ai": return renderAi();
      case "resume": return renderResume();
      case "security": return renderSecurity();
      case "about": return renderAbout();
    }
  };

  // ── Main Render ───────────────────────────────────────────

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
          <p className="mt-1 text-sm text-text-secondary">Configure your CareerForge AI experience</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/settings/updates")}
            icon={<Sparkles className="h-4 w-4" />}
          >
            Updates
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleResetAll}
            icon={<RotateCcw className="h-4 w-4" />}
          >
            Reset All
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-border pb-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.key
                ? "bg-surface-1 text-brand-600 border-b-2 border-brand-600"
                : "text-text-secondary hover:text-text-primary hover:bg-surface-1/50"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
}
