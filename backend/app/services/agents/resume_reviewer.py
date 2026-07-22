"""Resume Reviewer Agent — reviews and critiques resume quality."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class ResumeReviewerAgent(Agent):
    """Reviews resume quality and suggests improvements."""

    def __init__(self):
        super().__init__("resume_reviewer", max_retries=1)

    def system_prompt(self) -> str:
        return (
            "You are an expert resume reviewer. Critically evaluate this resume "
            "against the job requirements. Score each dimension 0-100: "
            "content_quality, relevance, clarity, impact, completeness. "
            "Provide specific improvement suggestions. "
            "Return JSON: {overall_score: number, scores: {content_quality, relevance, clarity, impact, completeness}, "
            "strengths: [...], weaknesses: [...], suggestions: [{priority, area, suggestion}], "
            "should_continue_reflection: boolean}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Resume:\n---\n{kwargs.get('resume_text', '')}\n---\n\n"
            f"Job Description:\n---\n{kwargs.get('job_description', '')}\n---"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
