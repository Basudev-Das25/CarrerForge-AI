"""Knowledge Retrieval Agent — retrieves relevant profile knowledge."""

from __future__ import annotations
from typing import Any
from app.services.agents.base import Agent


class KnowledgeRetrievalAgent(Agent):
    """Retrieves relevant knowledge from the knowledge graph for a given context."""

    def __init__(self):
        super().__init__("knowledge_retrieval", max_retries=1)

    def system_prompt(self) -> str:
        return (
            "You are a knowledge retrieval agent. Given a set of candidate knowledge items "
            "and a target job context, rank and select the most relevant items. "
            "For each item, explain WHY it's relevant. "
            "Return JSON: {ranked_items: [{id, type, relevance_reason, score, keywords}]} "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Target job: {kwargs.get('job_title', '')}\n"
            f"Required skills: {kwargs.get('required_skills', [])}\n"
            f"Available knowledge items:\n{kwargs.get('knowledge_items', '[]')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
