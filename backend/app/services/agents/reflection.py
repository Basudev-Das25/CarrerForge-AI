"""Reflection Agent — iteratively improves resume based on feedback."""

from __future__ import annotations
from typing import Any
from app.services.agents.base import Agent


class ReflectionAgent(Agent):
    """Improves resume through iterative reflection and refinement."""

    def __init__(self):
        super().__init__("reflection", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are a resume optimization expert. Improve the resume based on the "
            "evaluation feedback. Only modify what the feedback suggests. "
            "Preserve structure and tone. Naturally incorporate missing keywords. "
            "Never fabricate information. Track all changes. "
            "Return JSON: {improved_resume: string, changes_made: [{section, original, improved, reason}], "
            "keywords_added: [...], estimated_score_improvement: number}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Current Resume:\n---\n{kwargs.get('current_resume', '')}\n---\n\n"
            f"Evaluation Feedback:\n{kwargs.get('feedback_json', '{}')}\n\n"
            f"Target Keywords: {kwargs.get('target_keywords', [])}\n"
            f"Improvement Focus: {kwargs.get('improvement_focus', 'overall')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
