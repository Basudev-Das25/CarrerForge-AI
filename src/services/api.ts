/**
 * API client — wraps fetch calls to the FastAPI backend.
 */

import type {
  User, Education, Experience, Project, Skill,
  Certificate, Achievement, Language, Publication,
  Award, SocialLink, OriginalDocument,
} from "@/types";

const BASE_URL = "http://127.0.0.1:8000/api/v1";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) return undefined as T;
    return response.json();
  }

  // ── Health ──────────────────────────────────────────────

  async health() {
    return this.request<{ status: string; version: string }>("/health");
  }

  async config() {
    return this.request<{ ai_provider: string }>("/config");
  }

  // ── Profile ─────────────────────────────────────────────

  async getProfile() {
    return this.request<{ id: string; full_name: string | null; email: string | null; phone: string | null; location: string | null; linkedin_url: string | null; github_url: string | null; portfolio_url: string | null; summary: string | null; version: number; created_at: string; updated_at: string }>("/profile");
  }

  async updateProfile(data: Partial<User>) {
    return this.request<User>("/profile", { method: "PUT", body: JSON.stringify(data) });
  }

  async getDashboard() {
    return this.request<{
      profile: User | null;
      total_education: number;
      total_experience: number;
      total_projects: number;
      total_skills: number;
      total_certificates: number;
      total_achievements: number;
      total_languages: number;
      total_publications: number;
      total_awards: number;
      total_social_links: number;
      total_documents: number;
      total_resumes: number;
      profile_completion: number;
    }>("/dashboard");
  }

  async getCompletion() {
    return this.request<{ completion: number }>("/completion");
  }

  async globalSearch(query: string) {
    return this.request<{ query: string; results: Array<{ id: string; type: string; title: string; subtitle: string }> }>(`/search?q=${encodeURIComponent(query)}`);
  }

  // ── AI ──────────────────────────────────────────────────

  async getProviders() {
    return this.request<Array<{ name: string; id: string; models: string[] }>>("/ai/providers");
  }

  async chat(messages: Array<{ role: string; content: string }>, model?: string) {
    return this.request<{ content: string; model: string; usage: Record<string, number> }>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ messages, model }),
    });
  }

  // ── Keywords ────────────────────────────────────────────

  async extractKeywords(text: string) {
    return this.request<{
      must_include: string[];
      technologies: string[];
      nice_to_have: string[];
      all_keywords: string[];
    }>("/keywords/extract", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  // ── Education ───────────────────────────────────────────

  async listEducation() {
    return this.request<Education[]>("/education");
  }

  async createEducation(data: Record<string, unknown>) {
    return this.request("/education", { method: "POST", body: JSON.stringify(data) });
  }

  async updateEducation(id: string, data: Record<string, unknown>) {
    return this.request(`/education/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteEducation(id: string) {
    return this.request(`/education/${id}`, { method: "DELETE" });
  }

  // ── Experience ──────────────────────────────────────────

  async listExperience() {
    return this.request<Experience[]>("/experience");
  }

  async createExperience(data: Record<string, unknown>) {
    return this.request("/experience", { method: "POST", body: JSON.stringify(data) });
  }

  async updateExperience(id: string, data: Record<string, unknown>) {
    return this.request(`/experience/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteExperience(id: string) {
    return this.request(`/experience/${id}`, { method: "DELETE" });
  }

  // ── Projects ────────────────────────────────────────────

  async listProjects() {
    return this.request<Project[]>("/projects");
  }

  async createProject(data: Record<string, unknown>) {
    return this.request("/projects", { method: "POST", body: JSON.stringify(data) });
  }

  async updateProject(id: string, data: Record<string, unknown>) {
    return this.request(`/projects/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteProject(id: string) {
    return this.request(`/projects/${id}`, { method: "DELETE" });
  }

  // ── Skills ──────────────────────────────────────────────

  async listSkills() {
    return this.request<Skill[]>("/skills");
  }

  async createSkill(data: Record<string, unknown>) {
    return this.request("/skills", { method: "POST", body: JSON.stringify(data) });
  }

  async updateSkill(id: string, data: Record<string, unknown>) {
    return this.request(`/skills/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteSkill(id: string) {
    return this.request(`/skills/${id}`, { method: "DELETE" });
  }

  // ── Certificates ────────────────────────────────────────

  async listCertificates() {
    return this.request<Certificate[]>("/certificates");
  }

  async createCertificate(data: Record<string, unknown>) {
    return this.request("/certificates", { method: "POST", body: JSON.stringify(data) });
  }

  async updateCertificate(id: string, data: Record<string, unknown>) {
    return this.request(`/certificates/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteCertificate(id: string) {
    return this.request(`/certificates/${id}`, { method: "DELETE" });
  }

  // ── Achievements ────────────────────────────────────────

  async listAchievements() {
    return this.request<Achievement[]>("/achievements");
  }

  async createAchievement(data: Record<string, unknown>) {
    return this.request("/achievements", { method: "POST", body: JSON.stringify(data) });
  }

  async updateAchievement(id: string, data: Record<string, unknown>) {
    return this.request(`/achievements/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteAchievement(id: string) {
    return this.request(`/achievements/${id}`, { method: "DELETE" });
  }

  // ── Languages ───────────────────────────────────────────

  async listLanguages() {
    return this.request<Language[]>("/languages");
  }

  async createLanguage(data: Record<string, unknown>) {
    return this.request("/languages", { method: "POST", body: JSON.stringify(data) });
  }

  async updateLanguage(id: string, data: Record<string, unknown>) {
    return this.request(`/languages/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteLanguage(id: string) {
    return this.request(`/languages/${id}`, { method: "DELETE" });
  }

  // ── Publications ────────────────────────────────────────

  async listPublications() {
    return this.request<Publication[]>("/publications");
  }

  async createPublication(data: Record<string, unknown>) {
    return this.request("/publications", { method: "POST", body: JSON.stringify(data) });
  }

  async updatePublication(id: string, data: Record<string, unknown>) {
    return this.request(`/publications/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deletePublication(id: string) {
    return this.request(`/publications/${id}`, { method: "DELETE" });
  }

  // ── Awards ──────────────────────────────────────────────

  async listAwards() {
    return this.request<Award[]>("/awards");
  }

  async createAward(data: Record<string, unknown>) {
    return this.request("/awards", { method: "POST", body: JSON.stringify(data) });
  }

  async updateAward(id: string, data: Record<string, unknown>) {
    return this.request(`/awards/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteAward(id: string) {
    return this.request(`/awards/${id}`, { method: "DELETE" });
  }

  // ── Social Links ────────────────────────────────────────

  async listSocialLinks() {
    return this.request<SocialLink[]>("/social-links");
  }

  async createSocialLink(data: Record<string, unknown>) {
    return this.request("/social-links", { method: "POST", body: JSON.stringify(data) });
  }

  async updateSocialLink(id: string, data: Record<string, unknown>) {
    return this.request(`/social-links/${id}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteSocialLink(id: string) {
    return this.request(`/social-links/${id}`, { method: "DELETE" });
  }

  // ── Documents ───────────────────────────────────────────

  async listDocuments() {
    return this.request<OriginalDocument[]>("/documents/");
  }

  async getDocument(id: string) {
    return this.request<OriginalDocument>(`/documents/${id}`);
  }

  async uploadDocument(file: File, category?: string) {
    const form = new FormData();
    form.append("file", file);
    if (category) form.append("category", category);
    const resp = await fetch(`${this.baseUrl}/documents/upload`, {
      method: "POST",
      body: form,
    });
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(error.detail || `HTTP ${resp.status}`);
    }
    return resp.json() as Promise<OriginalDocument>;
  }

  async uploadMultiple(files: File[], category?: string) {
    const form = new FormData();
    for (const f of files) form.append("files", f);
    if (category) form.append("category", category);
    const resp = await fetch(`${this.baseUrl}/documents/upload/multiple`, {
      method: "POST",
      body: form,
    });
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(error.detail || `HTTP ${resp.status}`);
    }
    return resp.json() as Promise<{ uploaded: number; errors: number; results: Array<{ id: string; name: string; status: string }>; errors_detail: Array<{ name: string; error: string }> }>;
  }

  async deleteDocument(id: string) {
    return this.request(`/documents/${id}`, { method: "DELETE" });
  }

  async countDocuments() {
    return this.request<{ total: number }>("/documents/count");
  }

  async searchDocuments(query: string, topK: number = 5) {
    return this.request<{ results: unknown[]; query: string }>(
      `/documents/search?query=${encodeURIComponent(query)}&top_k=${topK}`,
      { method: "POST" },
    );
  }

  // ── Resumes ─────────────────────────────────────────────

  async listResumes() {
    return this.request<{ resumes: unknown[]; total: number }>("/resumes/");
  }

  async generateResume(jobDescription: string, template?: string) {
    return this.request<{ status: string; message: string }>("/resumes/generate", {
      method: "POST",
      body: JSON.stringify({ job_description: jobDescription, template_name: template }),
    });
  }

  // ── ATS ─────────────────────────────────────────────────

  async analyzeResumeLegacy(resumeId: string, jobDescription?: string) {
    return this.request<{ status: string; message: string }>("/ats/analyze", {
      method: "POST",
      body: JSON.stringify({ resume_id: resumeId, job_description: jobDescription }),
    });
  }

  // ── Resume Generator ─────────────────────────────────────

  async generateResumeFull(jobDescription: string, template: string = "modern", maxIterations: number = 3) {
    return this.request<Record<string, unknown>>("/resume/generate", {
      method: "POST",
      body: JSON.stringify({ job_description: jobDescription, template, max_iterations: maxIterations }),
    });
  }

  async generateResumeBlueprint(jobDescription: string) {
    return this.request<{ blueprint: Record<string, unknown> }>("/resume/blueprint", {
      method: "POST",
      body: JSON.stringify({ job_description: jobDescription }),
    });
  }

  async validateResume(resume: Record<string, unknown>, targetKeywords?: string[]) {
    return this.request<{ validation: Record<string, unknown> }>("/resume/validate", {
      method: "POST",
      body: JSON.stringify({ resume, target_keywords: targetKeywords || [] }),
    });
  }

  async listResumeTemplates() {
    return this.request<{ templates: Array<{ name: string; display_name: string; description: string; page_size: string }> }>("/resume/templates");
  }

  async renderResumeTemplate(template: string, resume: Record<string, unknown>) {
    return this.request<{ typst: string; template: string }>(`/resume/templates/${template}/render`, {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async listResumeVersions() {
    return this.request<{ total: number; versions: Array<{ id: string; title: string; template_name?: string; ats_score?: number; created_at: string }> }>("/resume/versions");
  }

  async getResumeVersion(id: string) {
    return this.request<Record<string, unknown>>(`/resume/versions/${id}`);
  }

  async deleteResumeVersion(id: string) {
    return this.request(`/resume/versions/${id}`, { method: "DELETE" });
  }

  async compareResumeVersions(v1: string, v2: string) {
    return this.request<Record<string, unknown>>(`/resume/versions/compare?v1=${v1}&v2=${v2}`, { method: "POST" });
  }

  async exportResumeTypst(resume: Record<string, unknown>, template: string = "modern") {
    return this.request<{ typst: string; format: string }>(`/resume/export/typst?template=${template}`, {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async exportResumeText(resume: Record<string, unknown>) {
    return this.request<{ text: string; format: string }>("/resume/export/text", {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async exportResumeMarkdown(resume: Record<string, unknown>) {
    return this.request<{ markdown: string; format: string }>("/resume/export/markdown", {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async compileResume(resume: Record<string, unknown>, _template: string = "modern") {
    return this.request<{ compile: Record<string, unknown>; typst: string }>("/resume/compile", {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async validateResumeTypst(resume: Record<string, unknown>, _template: string = "modern") {
    return this.request<{ valid: boolean; errors: Array<Record<string, unknown>> }>("/resume/validate-typst", {
      method: "POST",
      body: JSON.stringify(resume),
    });
  }

  async getResumeTemplateTheme(name: string) {
    return this.request<{ template: string; theme: Record<string, unknown> }>(`/resume/themes/${name}`);
  }

  // ── ATS Intelligence ──────────────────────────────────

  async analyzeResume(resume: Record<string, unknown>, jobProfile: Record<string, unknown>) {
    return this.request<{ report: Record<string, unknown> }>("/ats-intelligence/analyze", {
      method: "POST",
      body: JSON.stringify({ resume, job_profile: jobProfile }),
    });
  }

  async analyzeVersion(versionId: string) {
    return this.request<{ report: Record<string, unknown>; report_id: string }>(
      `/ats-intelligence/analyze-version/${versionId}`,
    );
  }

  async optimizeResume(resume: Record<string, unknown>, jobProfile: Record<string, unknown>, targetScore: number = 85, maxIterations: number = 3) {
    return this.request<{
      resume: Record<string, unknown>;
      plan: Record<string, unknown>;
      initial_score: number;
      final_score: number;
      improvement: number;
    }>("/ats-intelligence/optimize", {
      method: "POST",
      body: JSON.stringify({ resume, job_profile: jobProfile, target_score: targetScore, max_iterations: maxIterations }),
    });
  }

  async compareResumes(resumeA: Record<string, unknown>, resumeB: Record<string, unknown>, jobProfile?: Record<string, unknown>) {
    return this.request<{ comparison: Record<string, unknown> }>("/ats-intelligence/compare", {
      method: "POST",
      body: JSON.stringify({ resume_a: resumeA, resume_b: resumeB, job_profile: jobProfile }),
    });
  }

  async compareVersions(v1: string, v2: string) {
    return this.request<Record<string, unknown>>(
      `/ats-intelligence/compare-versions?v1=${v1}&v2=${v2}`,
      { method: "POST" },
    );
  }

  async listAtsReports(limit: number = 50) {
    return this.request<{ total: number; reports: Array<{ id: string; score: number; created_at: string }> }>(
      `/ats-intelligence/reports?limit=${limit}`,
    );
  }

  async getAtsReport(reportId: string) {
    return this.request<Record<string, unknown>>(`/ats-intelligence/reports/${reportId}`);
  }

  async exportAtsReport(reportId: string, format: string = "markdown") {
    return this.request<{ markdown?: string; json?: Record<string, unknown>; format: string }>(
      `/ats-intelligence/reports/${reportId}/export?format=${format}`,
      { method: "POST" },
    );
  }

  // ── Updates ──────────────────────────────────────────────

  async getCurrentVersion() {
    return this.request<{ version: string; build_number: number; platform: string; architecture: string; published_date: string }>("/updates/version");
  }

  async getUpdateChannels() {
    return this.request<{ channels: Array<{ name: string; display_name: string; description: string; base_url: string }> }>("/updates/channels");
  }

  async getUpdateSettings() {
    return this.request<Record<string, unknown>>("/updates/settings");
  }

  async updateSettings(settings: Record<string, unknown>) {
    return this.request<Record<string, unknown>>("/updates/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    });
  }

  async resetUpdateSettings() {
    return this.request<Record<string, unknown>>("/updates/settings/reset", { method: "POST" });
  }

  async getUpdateHistory() {
    return this.request<{ updates: Array<Record<string, unknown>>; total: number }>("/updates/history");
  }

  async getReleaseNotes() {
    return this.request<{ releases: Array<Record<string, unknown>> }>("/updates/release-notes");
  }

  async checkForUpdate() {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke("check_for_update");
    } catch {
      return { available: false, version: "" };
    }
  }

  async downloadUpdate() {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke("download_update");
    } catch {
      throw new Error("Download failed");
    }
  }

  async installUpdate() {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke("install_update");
    } catch {
      throw new Error("Install failed");
    }
  }

  // ── Backup ────────────────────────────────────────────────

  async listBackups() {
    return this.request<{ backups: Array<Record<string, unknown>>; total: number }>("/backup/");
  }

  async createBackup(description: string = "") {
    return this.request<{ backup: Record<string, unknown> }>("/backup/create", {
      method: "POST",
      body: JSON.stringify({ description }),
    });
  }

  async restoreBackup(backupId: string) {
    return this.request<{ restored_files: number }>("/backup/restore", {
      method: "POST",
      body: JSON.stringify({ backup_id: backupId }),
    });
  }

  async deleteBackup(backupId: string) {
    return this.request(`/backup/${backupId}`, { method: "DELETE" });
  }

  async exportBackup(backupId: string, exportPath: string) {
    return this.request<{ path: string }>("/backup/export", {
      method: "POST",
      body: JSON.stringify({ backup_id: backupId, export_path: exportPath }),
    });
  }

  async importBackup(importPath: string) {
    return this.request<{ backup: Record<string, unknown> }>("/backup/import", {
      method: "POST",
      body: JSON.stringify({ import_path: importPath }),
    });
  }

  // ── Diagnostics ──────────────────────────────────────────

  async getSystemInfo() {
    return this.request<Record<string, unknown>>("/diagnostics/system");
  }

  async healthCheck() {
    return this.request<Record<string, string>>("/diagnostics/health", { method: "POST" });
  }

  async getLogs(maxLines: number = 200) {
    return this.request<{ logs: string; log_files: string[] }>(`/diagnostics/logs?max_lines=${maxLines}`);
  }

  async clearLogs() {
    return this.request<{ cleared: number }>("/diagnostics/logs/clear", { method: "POST" });
  }

  async exportDiagnostics() {
    return this.request<{ path: string; message: string }>("/diagnostics/export", { method: "POST" });
  }
}

export const api = new ApiClient();
