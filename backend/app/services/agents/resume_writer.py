"""Resume Writer Agent — writes resume content for each section."""

from __future__ import annotations

from typing import Any

from app.services.agents.base import Agent


class ResumeWriterAgent(Agent):
    """Writes resume content for individual sections."""

    def __init__(self):
        super().__init__("resume_writer", max_retries=2)

    def system_prompt(self) -> str:
        return (
            "You are an expert resume writer. Write the specified resume section "
            "using the provided evidence and plan. "
            "Rules: Use strong action verbs, quantify achievements, "
            "incorporate ATS keywords naturally, match the specified tone, "
            "do NOT fabricate information. "
            "Return the section content as clean formatted text."
        )

    def user_prompt(self, **kwargs: Any) -> str:
        return (
            f"Section: {kwargs.get('section_name', '')}\n"
            f"Tone: {kwargs.get('tone', 'professional')}\n"
            f"Target words: {kwargs.get('word_count_target', 100)}\n"
            f"Key themes: {kwargs.get('key_themes', [])}\n"
            f"Evidence:\n{kwargs.get('evidence_json', '[]')}\n"
            f"Instructions: {kwargs.get('section_instructions', '')}"
        )

    def parse_response(self, raw: str) -> dict[str, Any]:
        return {"section_content": raw.strip()}

    def validate_output(self, data: dict[str, Any]) -> list[str]:
        content = data.get("section_content", "")
        if len(content) < 10:
            return ["Section content is too short"]
        return []
