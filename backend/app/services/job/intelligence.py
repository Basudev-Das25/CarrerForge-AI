"""Job Intelligence Engine — transforms raw JDs into structured job profiles.

Uses AI to parse, extract, and structure all relevant information from
job descriptions, enabling intelligent matching and resume tailoring.
"""

from __future__ import annotations

import json
import structlog
from typing import Any

from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole

logger = structlog.get_logger("careerforge.job.intelligence")


class JobProfile:
    """Structured representation of a parsed job description."""

    def __init__(self, data: dict[str, Any]):
        self.raw_data = data
        self.job_title: str = data.get("job_title", "")
        self.company: str = data.get("company", "")
        self.industry: str = data.get("industry", "")
        self.employment_type: str = data.get("employment_type", "full-time")
        self.work_mode: str = data.get("work_mode", "unknown")
        self.location: str = data.get("location", "")
        self.salary_range: str | None = data.get("salary_range")
        self.required_skills: list[str] = data.get("required_skills", [])
        self.preferred_skills: list[str] = data.get("preferred_skills", [])
        self.required_experience_years: int | None = data.get("required_experience_years")
        self.education_level: str | None = data.get("education_level")
        self.certifications: list[str] = data.get("certifications", [])
        self.responsibilities: list[str] = data.get("responsibilities", [])
        self.technologies: list[str] = data.get("technologies", [])
        self.soft_skills: list[str] = data.get("soft_skills", [])
        self.keywords: list[str] = data.get("keywords", [])
        self.ats_keywords: list[str] = data.get("ats_keywords", [])
        self.job_family: str = data.get("job_family", "")
        self.role_category: str = data.get("role_category", "")
        self.seniority: str = data.get("seniority", "mid")
        self.leadership_required: bool = data.get("leadership_required", False)
        self.communication_required: bool = data.get("communication_required", False)
        self.research_required: bool = data.get("research_required", False)
        self.cloud_required: bool = data.get("cloud_required", False)
        self.programming_languages: list[str] = data.get("programming_languages", [])
        self.frameworks: list[str] = data.get("frameworks", [])
        self.databases: list[str] = data.get("databases", [])
        self.devops_tools: list[str] = data.get("devops_tools", [])
        self.security_requirements: list[str] = data.get("security_requirements", [])
        self.ai_ml_requirements: list[str] = data.get("ai_ml_requirements", [])
        self.summary: str = data.get("summary", "")

    def to_dict(self) -> dict[str, Any]:
        return self.raw_data

    def all_skills(self) -> set[str]:
        """Get all skills (required + preferred + technologies + programming languages)."""
        skills = set()
        skills.update(self.required_skills)
        skills.update(self.preferred_skills)
        skills.update(self.technologies)
        skills.update(self.programming_languages)
        skills.update(self.frameworks)
        skills.update(self.databases)
        skills.update(self.devops_tools)
        return skills

    def text_representation(self) -> str:
        """Full text representation for embedding."""
        parts = [
            self.job_title, self.company, self.industry, self.summary,
            " ".join(self.required_skills), " ".join(self.preferred_skills),
            " ".join(self.technologies), " ".join(self.responsibilities),
            " ".join(self.keywords),
        ]
        return " ".join(p for p in parts if p)


class JobIntelligence:
    """Parses and structures job descriptions using AI."""

    def __init__(self):
        self._parser_prompt = "jd/parser"
        self._extractor_prompt = "jd/extractor"

    async def parse_job_description(self, raw_text: str) -> JobProfile:
        """Parse a raw job description into a structured JobProfile.

        Uses AI to extract all relevant fields from unstructured text.
        """
        logger.info("job.parse.start", text_length=len(raw_text))

        try:
            response = await orchestrator.chat(
                messages=[
                    ChatMessage(
                        role=MessageRole.SYSTEM,
                        content=(
                            "You are an expert job description parser. "
                            "Extract ALL structured information from the job description. "
                            "Return a JSON object with these fields: "
                            "job_title, company, industry, employment_type, work_mode, location, "
                            "salary_range, required_skills, preferred_skills, "
                            "required_experience_years, education_level, certifications, "
                            "responsibilities, technologies, soft_skills, keywords, ats_keywords, "
                            "job_family, role_category, seniority, leadership_required, "
                            "communication_required, research_required, cloud_required, "
                            "programming_languages, frameworks, databases, devops_tools, "
                            "security_requirements, ai_ml_requirements, summary. "
                            "Return ONLY valid JSON."
                        ),
                    ),
                    ChatMessage(
                        role=MessageRole.USER,
                        content=f"Parse this job description:\n\n---\n{raw_text}\n---",
                    ),
                ],
                temperature=0.1,
                max_tokens=4096,
                use_cache=False,
            )

            # Parse JSON response
            parsed = self._parse_json_response(response.content)
            profile = JobProfile(parsed)
            logger.info("job.parse.complete", title=profile.job_title, company=profile.company)
            return profile

        except Exception as e:
            logger.error("job.parse.error", error=str(e))
            # Return a minimal profile from heuristic extraction
            return self._heuristic_parse(raw_text)

    async def extract_requirements(self, raw_text: str) -> dict[str, Any]:
        """Extract key requirements from a job description."""
        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "Extract ALL requirements from this job description. "
                        "Return JSON with: must_have_skills, nice_to_have_skills, "
                        "experience_years, education, certifications, soft_skills, keywords. "
                        "Return ONLY valid JSON."
                    ),
                ),
                ChatMessage(role=MessageRole.USER, content=raw_text),
            ],
            temperature=0.1,
            max_tokens=2048,
        )
        return self._parse_json_response(response.content)

    async def classify_job(self, raw_text: str) -> dict[str, str]:
        """Classify a job description into family, category, and seniority."""
        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "Classify this job. Return JSON with: "
                        "job_family, role_category, seniority level. "
                        "Return ONLY valid JSON."
                    ),
                ),
                ChatMessage(role=MessageRole.USER, content=raw_text),
            ],
            temperature=0.1,
            max_tokens=512,
        )
        return self._parse_json_response(response.content)

    async def match_candidate(
        self,
        job_profile: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Match a candidate profile against a job profile."""
        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "Analyze how well this candidate matches this job. "
                        "Return JSON with: match_score (0-100), matching_skills, "
                        "missing_skills, matching_experience, gaps, recommendation. "
                        "Return ONLY valid JSON."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=f"JOB: {json.dumps(job_profile)}\n\nCANDIDATE: {json.dumps(candidate_profile)}",
                ),
            ],
            temperature=0.2,
            max_tokens=2048,
        )
        return self._parse_json_response(response.content)

    def _parse_json_response(self, text: str) -> dict:
        """Extract and parse JSON from AI response."""
        text = text.strip()
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        # Try to find JSON in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        # Try array
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        logger.warning("job.parse.json_error", text_preview=text[:200])
        return {"error": "Failed to parse AI response", "raw": text}

    def _heuristic_parse(self, raw_text: str) -> JobProfile:
        """Fallback heuristic parsing when AI fails."""
        lines = raw_text.strip().split("\n")
        title = lines[0].strip() if lines else "Unknown Position"
        return JobProfile({
            "job_title": title,
            "summary": raw_text[:500],
            "raw_text": raw_text,
        })
