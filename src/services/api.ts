/**
 * API client — wraps fetch calls to the FastAPI backend.
 */

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

    return response.json();
  }

  // ── Health ──────────────────────────────────────────────

  async health() {
    return this.request<{ status: string; version: string }>("/health");
  }

  async config() {
    return this.request<{ ai_provider: string }>("/config");
  }

  // ── AI ──────────────────────────────────────────────────

  async getProviders() {
    return this.request<Array<{ name: string; id: string; models: string[] }>>("/ai/providers");
  }

  async chat(messages: Array<{ role: string; content: string }>, model?: string) {
    return this.request<{ content: string; model: string; usage: Record<string, number> }>(
      "/ai/chat",
      {
        method: "POST",
        body: JSON.stringify({ messages, model }),
      },
    );
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
}

export const api = new ApiClient();
