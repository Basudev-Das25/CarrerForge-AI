/**
 * API client — wraps fetch calls to the FastAPI backend.
 */

import type {
  User, Education, Experience, Project, Skill,
  Certificate, Achievement, Language, Publication,
  Award, SocialLink,
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
    return this.request<{ documents: unknown[]; total: number }>("/documents/");
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

  async analyzeResume(resumeId: string, jobDescription?: string) {
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
}

export const api = new ApiClient();
