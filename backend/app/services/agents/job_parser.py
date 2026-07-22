"""Job Parser Agent — parses raw job descriptions into structured profiles."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class JobParserAgent(Agent):
    """Parses raw job descriptions into structured job profiles."""

    def __init__(self):
        super().__init__("job_parser", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an expert job description parser for CareerForge AI. "
            "Extract ALL structured information from the job description. "
            "Return a JSON object with: job_title, company, industry, employment_type, "
            "work_mode, location, salary_range, required_skills, preferred_skills, "
            "required_experience_years, education_level, certifications, responsibilities, "
            "technologies, soft_skills, keywords, ats_keywords, job_family, role_category, "
            "seniority, leadership_required, communication_required, research_required, "
            "cloud_required, programming_languages, frameworks, databases, devops_tools, "
            "security_requirements, ai_ml_requirements, summary. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return f"Parse this job description:\n\n---\n{kwargs.get('job_description', '')}\n---"

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)

    def validate_input(self, **kwargs: Any) -> list[str]:
        issues = []
        if not kwargs.get("job_description"):
            issues.append("job_description is required")
        elif len(kwargs["job_description"]) < 20:
            issues.append("job_description is too short (min 20 chars)")
        return issues
