"""Interview Agent — prepares interview questions and talking points."""

from __future__ import annotations
from typing import Any
from app.services.agents.base import Agent


class InterviewAgent(Agent):
    """Prepares interview questions and talking points."""

    def __init__(self):
        super().__init__("interview", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an interview preparation coach. Given a job profile and candidate background, "
            "generate: 1) Likely interview questions with suggested answers, "
            "2) Technical questions based on required skills, "
            "3) Behavioral questions with STAR-formatted answers, "
            "4) Talking points about key achievements, "
            "5) Questions the candidate should ask the interviewer. "
            "Return JSON: {questions: [{question, answer, category, difficulty}], "
            "talking_points: [...], questions_to_ask: [...]}. "
            "Return ONLY valid JSON."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Job: {kwargs.get('job_title', '')} at {kwargs.get('company', '')}\n"
            f"Skills Required: {kwargs.get('required_skills', [])}\n"
            f"Candidate Background:\n{kwargs.get('candidate_summary', '')}\n"
            f"Key Achievements: {kwargs.get('achievements', [])}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return self._parse_json(raw)
