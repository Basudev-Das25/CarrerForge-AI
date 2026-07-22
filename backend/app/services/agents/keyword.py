"""Keyword Agent — extracts and ranks ATS keywords."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class KeywordAgent(Agent):
    """Extracts and ranks important ATS keywords from job descriptions."""

    def __init__(self):
        super().__init__("keyword", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an ATS keyword optimization expert. "
            "Extract the most important keywords from this job description "
            "that a resume MUST include to pass ATS screening. "
            "Rank them by importance. Return JSON: "
            "{primary_keywords: [...], secondary_keywords: [...], "
            "technical_terms: [...], soft_skill_keywords: [...], "
            "industry_terms: [...]}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return f"Extract ATS keywords from:\n\n{kwargs.get('job_description', '')}"

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)

    def validate_input(self, **kwargs: Any) -> list[str]:
        if not kwargs.get("job_description"):
            return ["job_description is required"]
        return []
