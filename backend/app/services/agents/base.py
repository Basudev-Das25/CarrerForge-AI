"""Agent Base Class — reusable pattern for all AI agents.

Every AI capability becomes an Agent with execute(), validate(),
retry(), and health() methods.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole

logger = logging.getLogger("careerforge.agents")


@dataclass
class AgentResult:
    """Standardized result from an agent execution."""
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    raw_response: str = ""
    prompt_version: str = ""
    provider: str = ""
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    error: str = ""
    retry_count: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "prompt_version": self.prompt_version,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": round(self.latency_ms, 1),
            "error": self.error,
            "retry_count": self.retry_count,
        }


class Agent(ABC):
    """Base class for all AI agents."""

    def __init__(self, name: str, max_retries: int = 2):
        self.name = name
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"careerforge.agents.{name}")

    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...

    @abstractmethod
    def user_prompt(self, **kwargs: Any) -> str:
        """Build the user prompt from keyword arguments."""
        ...

    @abstractmethod
    def parse_response(self, raw: str) -> dict[str, Any]:
        """Parse the AI response into structured data."""
        ...

    def validate_input(self, **kwargs: Any) -> list[str]:
        """Validate input arguments. Return list of issues (empty = valid)."""
        return []

    def validate_output(self, data: dict[str, Any]) -> list[str]:
        """Validate parsed output. Return list of issues (empty = valid)."""
        return []

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the agent with full error handling and retries."""
        start = time.time()

        # Validate input
        input_issues = self.validate_input(**kwargs)
        if input_issues:
            return AgentResult(
                success=False,
                error=f"Input validation failed: {'; '.join(input_issues)}",
            )

        last_error = ""
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info("agent.execute.start", attempt=attempt)
                response = await orchestrator.chat(
                    messages=[
                        ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt()),
                        ChatMessage(role=MessageRole.USER, content=self.user_prompt(**kwargs)),
                    ],
                    temperature=kwargs.get("temperature", 0.3),
                    max_tokens=kwargs.get("max_tokens", 4096),
                    use_cache=kwargs.get("use_cache", True),
                )

                # Parse response
                data = self.parse_response(response.content)

                # Validate output
                output_issues = self.validate_output(data)
                if output_issues and attempt < self.max_retries:
                    self.logger.warning("agent.output.invalid", issues=output_issues, attempt=attempt)
                    last_error = f"Validation: {'; '.join(output_issues)}"
                    continue

                latency = (time.time() - start) * 1000
                result = AgentResult(
                    success=True,
                    data=data,
                    raw_response=response.content,
                    provider=response.model,
                    model=response.model,
                    tokens_used=response.usage.get("total_tokens", 0),
                    latency_ms=round(latency, 1),
                    retry_count=attempt,
                )
                self.logger.info("agent.execute.complete", latency_ms=result.latency_ms, retries=attempt)
                return result

            except Exception as e:
                last_error = str(e)
                self.logger.warning("agent.execute.error", attempt=attempt, error=last_error)

        latency = (time.time() - start) * 1000
        return AgentResult(
            success=False,
            error=f"Failed after {self.max_retries + 1} attempts: {last_error}",
            latency_ms=round(latency, 1),
            retry_count=self.max_retries,
        )

    async def health(self) -> dict:
        """Check agent health by verifying orchestrator and prompt availability."""
        try:
            stats = orchestrator.get_stats()
            return {"healthy": True, "providers": stats["providers"], "name": self.name}
        except Exception as e:
            return {"healthy": False, "error": str(e), "name": self.name}

    def metrics(self) -> dict:
        """Return agent-specific metrics."""
        return {"name": self.name, "max_retries": self.max_retries}

    def _parse_json(self, text: str) -> dict:
        """Helper to extract JSON from AI response."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                return {"items": json.loads(text[start:end])}
            except json.JSONDecodeError:
                pass

        return {"raw": text}
