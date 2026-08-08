import { useEffect, useState } from "react";
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  ArrowUpCircle,
  Download,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */

interface UpdateSettings {
  enabled: boolean;
  check_on_startup: boolean;
  check_interval: string;
  download_automatically: boolean;
  install_automatically: boolean;
  install_on_restart: boolean;
  channel: string;
  allow_metered_downloads: boolean;
  skipped_versions: string[];
  last_check_date: string | null;
}

interface UpdateInfo {
  version: string;
  available: boolean;
  release_notes: string;
  download_url: string;
}

interface HistoryEntry {
  version: string;
  timestamp: string;
  success: boolean;
  error: string;
}

export default function UpdateSettingsScreen() {
  const [settings, setSettings] = useState<UpdateSettings>({
    enabled: true, check_on_startup: true, check_interval: "weekly",
    download_automatically: false, install_automatically: false,
    install_on_restart: true, channel: "stable", allow_metered_downloads: false,
    skipped_versions: [], last_check_date: null,
  });
  const [currentVersion, setCurrentVersion] = useState("");
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [checking, setChecking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [channels, setChannels] = useState<Array<{ name: string; display_name: string; description: string }>>([]);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [s, v, h, ch] = await Promise.all([
        api.getUpdateSettings(),
        api.getCurrentVersion(),
        api.getUpdateHistory(),
        api.getUpdateChannels(),
      ]);
      setSettings(s as any);
      setCurrentVersion((v as any).version);
      setHistory((h.updates as any) || []);
      setChannels((ch as any).channels || []);
    } catch { /* ignore */ }
  };

  const handleCheck = async () => {
    setChecking(true);
    try {
      const info = await api.checkForUpdate();
      setUpdateInfo(info as any);
      if ((info as any).available) {
        toast.success(`Update available: v${(info as any).version}`);
      } else {
        toast.success("You're up to date!");
      }
    } catch {
      toast.error("Update check failed");
    } finally {
      setChecking(false);
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await api.downloadUpdate();
      toast.success("Update downloaded — restart to install");
    } catch {
      toast.error("Download failed");
    } finally {
      setDownloading(false);
    }
  };

  const handleInstall = async () => {
    await api.installUpdate();
  };

  const updateSetting = async (key: string, value: any) => {
    const updated = { ...settings, [key]: value } as UpdateSettings;
    setSettings(updated);
    try {
      await api.updateSettings({ ...updated, skipped_versions: updated.skipped_versions });
    } catch {
      toast.error("Failed to save setting");
    }
  };

  const handleReset = async () => {
    try {
      const s = await api.resetUpdateSettings();
      setSettings(s as any);
      toast.success("Settings reset to defaults");
    } catch {
      toast.error("Failed to reset");
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Updates</h1>
        <p className="mt-1 text-sm text-text-secondary">Keep CareerForge AI up to date</p>
      </div>

      {/* Current Version */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-text-primary">Current Version</h3>
            <p className="text-sm text-text-tertiary">Version {currentVersion}</p>
          </div>
          <span className="badge badge-success">Installed</span>
        </div>
      </div>

      {/* Check for Updates */}
      <div className="card space-y-4">
        <h3 className="section-title">Check for Updates</h3>
        <p className="section-description">Check if a newer version is available</p>
        <Button onClick={handleCheck} loading={checking} icon={<RefreshCw className="h-4 w-4" />}>
          Check for Updates
        </Button>
        {updateInfo?.available && (
          <div className="mt-4 p-4 rounded-lg border border-green-300 bg-green-50 dark:bg-green-950 dark:border-green-800">
            <div className="flex items-center gap-3">
              <ArrowUpCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800 dark:text-green-200">Update Available: v{updateInfo.version}</p>
                {updateInfo.release_notes && (
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">{updateInfo.release_notes}</p>
                )}
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              <Button size="sm" onClick={handleDownload} loading={downloading} icon={<Download className="h-3.5 w-3.5" />}>
                Download
              </Button>
              <Button size="sm" variant="secondary" onClick={handleInstall} icon={<CheckCircle className="h-3.5 w-3.5" />}>
                Install & Restart
              </Button>
            </div>
          </div>
        )}
        {updateInfo && !updateInfo.available && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">You're running the latest version</span>
          </div>
        )}
      </div>

      {/* Update Settings */}
      <div className="card space-y-4">
        <h3 className="section-title">Update Settings</h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-medium text-text-primary">Enable Automatic Updates</p>
              <p className="text-xs text-text-tertiary">Allow the app to check for updates automatically</p>
            </div>
            <button onClick={() => updateSetting("enabled", !settings.enabled)}
              className={`relative w-11 h-6 rounded-full transition-colors ${settings.enabled ? "bg-brand-600" : "bg-surface-3"}`}>
              <span className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform shadow ${settings.enabled ? "translate-x-5" : ""}`} />
            </button>
          </div>

          {settings.enabled && (
            <>
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">Check on Startup</p>
                  <p className="text-xs text-text-tertiary">Check for updates when the app starts</p>
                </div>
                <button onClick={() => updateSetting("check_on_startup", !settings.check_on_startup)}
                  className={`relative w-11 h-6 rounded-full transition-colors ${settings.check_on_startup ? "bg-brand-600" : "bg-surface-3"}`}>
                  <span className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform shadow ${settings.check_on_startup ? "translate-x-5" : ""}`} />
                </button>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">Check Frequency</p>
                  <p className="text-xs text-text-tertiary">How often to check for updates</p>
                </div>
                <select value={settings.check_interval} onChange={(e) => updateSetting("check_interval", e.target.value)}
                  className="input text-sm py-1 w-32">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">Update Channel</p>
                  <p className="text-xs text-text-tertiary">Stable is recommended</p>
                </div>
                <select value={settings.channel} onChange={(e) => updateSetting("channel", e.target.value)}
                  className="input text-sm py-1 w-32">
                  {channels.map((ch) => (
                    <option key={ch.name} value={ch.name}>{ch.display_name}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">Download Automatically</p>
                  <p className="text-xs text-text-tertiary">Download updates in the background</p>
                </div>
                <button onClick={() => updateSetting("download_automatically", !settings.download_automatically)}
                  className={`relative w-11 h-6 rounded-full transition-colors ${settings.download_automatically ? "bg-brand-600" : "bg-surface-3"}`}>
                  <span className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform shadow ${settings.download_automatically ? "translate-x-5" : ""}`} />
                </button>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">Install on Next Restart</p>
                  <p className="text-xs text-text-tertiary">Apply updates when you restart the app</p>
                </div>
                <button onClick={() => updateSetting("install_on_restart", !settings.install_on_restart)}
                  className={`relative w-11 h-6 rounded-full transition-colors ${settings.install_on_restart ? "bg-brand-600" : "bg-surface-3"}`}>
                  <span className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform shadow ${settings.install_on_restart ? "translate-x-5" : ""}`} />
                </button>
              </div>
            </>
          )}

          <div className="pt-4 border-t border-border">
            <Button variant="secondary" size="sm" onClick={handleReset}>Reset to Defaults</Button>
          </div>
        </div>
      </div>

      {/* Update History */}
      <div className="card space-y-4">
        <h3 className="section-title">Update History</h3>
        {history.length === 0 ? (
          <p className="text-sm text-text-tertiary">No updates installed yet</p>
        ) : (
          <div className="space-y-2">
            {history.slice(0, 3).map((entry, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div className="flex items-center gap-2">
                  {entry.success ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                  <span className="text-sm text-text-primary">v{entry.version}</span>
                  <span className="text-xs text-text-tertiary">{new Date(entry.timestamp).toLocaleDateString()}</span>
                </div>
                {!entry.success && entry.error && <span className="text-xs text-red-500">{entry.error}</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Release Notes */}
      <div className="card space-y-4">
        <h3 className="section-title">Release Notes</h3>
        <div className="space-y-3">
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="badge badge-success text-xs">Latest</span>
              <span className="font-semibold text-text-primary">v0.1.1</span>
              <span className="text-xs text-text-tertiary">July 22, 2026</span>
            </div>
            <ul className="text-sm text-text-secondary space-y-1">
              <li>• Complete profile management with 12 entity types</li>
              <li>• Knowledge engine with semantic search and scoring</li>
              <li>• AI-powered resume generation pipeline</li>
              <li>• 4 production-ready Typst resume templates</li>
              <li>• ATS intelligence with scoring and optimization</li>
              <li>• Multi-provider AI orchestration</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
