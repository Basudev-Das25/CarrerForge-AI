"""Skill Extraction Agent — extracts skills from text and profiles."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class SkillExtractionAgent(Agent):
    """Extracts and categorizes skills from various sources."""

    def __init__(self):
        super().__init__("skill_extraction", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are a skill extraction expert. Extract all skills from the text. "
            "For each skill, provide: name, category (programming/framework/tool/soft/domain), "
            "proficiency_level (beginner/intermediate/advanced/expert), and confidence (0-1). "
            "Return JSON: {skills: [{name, category, proficiency_level, confidence}]}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        text = kwargs.get("text", "")
        context = kwargs.get("context", "")
        prompt = f"Extract skills from:\n\n{text}"
        if context:
            prompt += f"\n\nContext: {context}"
        return prompt

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
