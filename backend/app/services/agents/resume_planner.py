"""Resume Planner Agent — plans resume structure and content allocation."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class ResumePlannerAgent(Agent):
    """Plans the optimal resume structure for a given job and evidence."""

    def __init__(self):
        super().__init__("resume_planner", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an expert resume strategist. Given a job profile and candidate evidence, "
            "plan the optimal resume structure. Specify sections, order, emphasis areas, "
            "ATS keywords to include, and word count targets per section. "
            "Return JSON: {sections: [{name, priority, word_count_target, key_themes, evidence_ids}], "
            "emphasis_areas: [...], ats_keywords_to_include: [...], tone: string, "
            "estimated_total_words: number}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Job Profile:\n{kwargs.get('job_profile_json', '{}')}\n\n"
            f"Evidence Bundle:\n{kwargs.get('evidence_bundle_json', '{}')}\n\n"
            f"Template Style: {kwargs.get('template_style', 'modern-professional')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
