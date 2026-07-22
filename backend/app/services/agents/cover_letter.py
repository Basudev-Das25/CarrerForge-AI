"""Cover Letter Agent — generates tailored cover letters."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class CoverLetterAgent(Agent):
    """Generates tailored cover letters for job applications."""

    def __init__(self):
        super().__init__("cover_letter", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an expert cover letter writer. Write a compelling, personalized "
            "cover letter for this job application. Structure: opening hook, "
            "body paragraphs connecting experience to requirements, closing call to action. "
            "Tone: professional but personable. Length: 250-400 words. "
            "Return the cover letter as formatted text."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Candidate: {kwargs.get('candidate_name', '')}\n"
            f"Summary: {kwargs.get('candidate_summary', '')}\n"
            f"Key Skills: {kwargs.get('key_skills', [])}\n"
            f"Notable Achievements: {kwargs.get('achievements', [])}\n\n"
            f"Job: {kwargs.get('job_title', '')} at {kwargs.get('company', '')}\n"
            f"Requirements: {kwargs.get('requirements', [])}\n"
            f"Company Info: {kwargs.get('company_info', '')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return {"cover_letter": raw.strip()}
