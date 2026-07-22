"""ATS Evaluator Agent — evaluates resume against ATS scoring criteria."""

from __future__ import annotations
from typing import Any
from app.services.agents.base import Agent


class ATSEvaluatorAgent(Agent):
    """Evaluates resume ATS compatibility and scoring."""

    def __init__(self):
        super().__init__("ats_evaluator", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an ATS (Applicant Tracking System) expert evaluator. "
            "Score this resume against the job description across 5 dimensions (0-100): "
            "keyword_score, formatting_score, impact_score, readability_score, coverage_score. "
            "List missing keywords and provide improvement suggestions. "
            "Return JSON: {overall_score: number, keyword_score: number, formatting_score: number, "
            "impact_score: number, readability_score: number, coverage_score: number, "
            "missing_keywords: [...], suggestions: [...], strengths: [...], weak_areas: [...]}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Resume:\n---\n{kwargs.get('resume_text', '')}\n---\n\n"
            f"Job Description:\n---\n{kwargs.get('job_description', '')}\n---\n\n"
            f"ATS Keywords to check: {kwargs.get('ats_keywords', [])}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)

    def validate_input(self, **kwargs: Any) -> list[str]:
        issues = []
        if not kwargs.get("resume_text"):
            issues.append("resume_text is required")
        if not kwargs.get("job_description"):
            issues.append("job_description is required")
        return issues
