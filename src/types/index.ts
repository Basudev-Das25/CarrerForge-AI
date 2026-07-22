/**
 * CareerForge AI — Shared TypeScript type definitions.
 * These types mirror the backend SQLAlchemy models.
 */

// ── User / Profile ──────────────────────────────────────────

export interface User {
  id: string;
  email?: string;
  full_name?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  summary?: string;
  avatar_path?: string;
  version: number;
  created_at: string;
  updated_at: string;
}

// ── Education ───────────────────────────────────────────────

export interface Education {
  id: string;
  user_id: string;
  degree: string;
  field_of_study?: string;
  institution: string;
  location?: string;
  start_date: string;
  end_date?: string;
  gpa?: number;
  description?: string;
  highlights: string[];
}

// ── Experience ──────────────────────────────────────────────

export type EmploymentType = "full-time" | "part-time" | "contract" | "internship" | "freelance";

export interface Experience {
  id: string;
  user_id: string;
  company: string;
  title: string;
  location?: string;
  employment_type?: EmploymentType;
  start_date: string;
  end_date?: string;
  description?: string;
  highlights: string[];
  skills_used: string[];
}

// ── Projects ────────────────────────────────────────────────

export type ProjectDifficulty = "beginner" | "intermediate" | "advanced" | "expert";
export type ProjectStatus = "planning" | "in-progress" | "completed" | "archived";

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  role?: string;
  repo_url?: string;
  live_url?: string;
  tech_stack: string[];
  industry?: string;
  category?: string;
  team_size?: number;
  difficulty?: ProjectDifficulty;
  tags: string[];
  keywords: string[];
  responsibilities: string[];
  impact_metrics: string[];
  skills_used: string[];
  highlights: string[];
  visibility: "private" | "public";
  status: ProjectStatus;
  start_date?: string;
  end_date?: string;
  is_featured: boolean;
}

// ── Skills ──────────────────────────────────────────────────

export type SkillCategory = "programming" | "framework" | "tool" | "soft" | "domain";
export type SkillLevel = "beginner" | "intermediate" | "advanced" | "expert";

export interface Skill {
  id: string;
  user_id: string;
  name: string;
  category?: SkillCategory;
  subcategory?: string;
  level?: SkillLevel;
  years_experience?: number;
  last_used?: string;
  is_primary: boolean;
}

// ── Certificates ────────────────────────────────────────────

export type CertificateVerification = "unverified" | "pending" | "verified" | "expired";

export interface Certificate {
  id: string;
  user_id: string;
  title: string;
  issuer: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
  skills: string[];
  level?: string;
  tags: string[];
  verification_status: CertificateVerification;
  related_project_ids: string[];
}

// ── Achievements ────────────────────────────────────────────

export type AchievementCategory = "award" | "publication" | "patent" | "speaking" | "other";

export interface Achievement {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  date?: string;
  category?: AchievementCategory;
  organization?: string;
  url?: string;
}

// ── Languages ───────────────────────────────────────────────

export type LanguageProficiency = "native" | "fluent" | "advanced" | "intermediate" | "beginner";

export interface Language {
  id: string;
  user_id: string;
  name: string;
  proficiency?: LanguageProficiency;
  years?: number;
  is_native: boolean;
}

// ── Publications ────────────────────────────────────────────

export type PublicationCategory = "journal" | "conference" | "workshop" | "preprint" | "book" | "other";

export interface Publication {
  id: string;
  user_id: string;
  title: string;
  authors: string[];
  venue?: string;
  date?: string;
  url?: string;
  doi?: string;
  description?: string;
  category?: PublicationCategory;
}

// ── Awards ──────────────────────────────────────────────────

export type AwardCategory = "academic" | "professional" | "competition" | "community" | "other";

export interface Award {
  id: string;
  user_id: string;
  title: string;
  issuer?: string;
  date?: string;
  category?: AwardCategory;
  description?: string;
  url?: string;
}

// ── Social Links ────────────────────────────────────────────

export interface SocialLink {
  id: string;
  user_id: string;
  platform: string;
  url: string;
  username?: string;
  display_name?: string;
}

// ── Resume Versions ─────────────────────────────────────────

export interface ResumeVersion {
  id: string;
  user_id: string;
  title: string;
  template_name?: string;
  content_json?: Record<string, unknown>;
  pdf_path?: string;
  ats_score?: number;
  reflection_iterations: number;
  job_description_id?: string;
  is_final: boolean;
  created_at: string;
}

// ── ATS Reports ─────────────────────────────────────────────

export interface ATSReport {
  id: string;
  resume_version_id: string;
  score: number;
  keyword_score?: number;
  formatting_score?: number;
  impact_score?: number;
  readability_score?: number;
  coverage_score?: number;
  report_json?: Record<string, unknown>;
  suggestions: string[];
  created_at: string;
}

// ── Job Descriptions ────────────────────────────────────────

export interface JobDescription {
  id: string;
  user_id: string;
  title?: string;
  company?: string;
  raw_text: string;
  parsed_json?: Record<string, unknown>;
  keywords: string[];
  requirements: string[];
  created_at: string;
}

// ── Original Documents ──────────────────────────────────────

export type DocumentCategory = "resume" | "certificate" | "reference" | "other";

export interface OriginalDocument {
  id: string;
  file_path: string;
  original_name: string;
  mime_type?: string;
  file_size?: number;
  text_content?: string;
  metadata_json?: Record<string, unknown>;
  category?: DocumentCategory;
  embedding_ids: string[];
  ocr_performed: boolean;
  created_at: string;
}

// ── AI Provider ─────────────────────────────────────────────

export type ProviderID = "openai" | "claude" | "openrouter" | "grok" | "huggingface" | "ollama";

export interface ProviderInfo {
  name: string;
  id: ProviderID;
  models: string[];
}

// ── Search ──────────────────────────────────────────────────

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  subtitle: string;
}

// ── Settings ────────────────────────────────────────────────

export interface AppSettings {
  ai_provider: ProviderID;
  theme: "light" | "dark" | "system";
  max_reflection_iterations: number;
  ats_score_threshold: number;
  default_template: string;
  onboarding_complete: boolean;
}
