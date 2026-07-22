"""Evidence Agent — generates evidence bundles from knowledge."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class EvidenceAgent(Agent):
    """Selects and scores evidence items for resume generation."""

    def __init__(self):
        super().__init__("evidence", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an evidence selection agent. Given candidate evidence items "
            "and a job profile, select the best evidence for a resume. "
            "For each selected item, provide: entity_type, entity_id, reason, "
            "confidence (0-1), keywords_used. "
            "Return JSON: {selected: [{entity_type, entity_id, reason, confidence, keywords_used}]} "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Job: {kwargs.get('job_title', '')} at {kwargs.get('company', '')}\n"
            f"Required skills: {kwargs.get('required_skills', [])}\n"
            f"Evidence items:\n{kwargs.get('evidence_items', '[]')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
