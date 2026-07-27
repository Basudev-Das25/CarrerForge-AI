"""Provider base class — abstract interface for all AI providers.

Every provider must implement these methods for the orchestrator
to manage them uniformly.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    cached: bool = False


@dataclass
class EmbeddingResponse:
    embedding: list[float]
    model: str
    dimensions: int = 0
    usage: dict[str, int] = field(default_factory=dict)


@dataclass
class ProviderHealth:
    healthy: bool
    latency_ms: float = 0.0
    error: str = ""
    models_available: list[str] = field(default_factory=list)


class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'openai', 'anthropic')."""
        ...

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """List of supported model IDs."""
        ...

    @property
    def default_model(self) -> str:
        """Default model to use."""
        return self.supported_models[0] if self.supported_models else ""

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send a chat completion request."""
        ...

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat completion. Default: non-streaming fallback."""
        response = await self.chat(messages, model, temperature, max_tokens, **kwargs)
        yield response.content

    async def generate_embedding(
        self,
        text: str,
        model: str | None = None,
    ) -> EmbeddingResponse:
        """Generate an embedding vector. Not all providers support this."""
        raise NotImplementedError(f"{self.name} does not support embeddings")

    async def health_check(self) -> ProviderHealth:
        """Check provider health. Default: try a simple chat."""
        start = time.time()
        try:
            await self.chat(
                [ChatMessage(role=MessageRole.USER, content="Say 'ok'")],
                max_tokens=10,
            )
            latency = (time.time() - start) * 1000
            return ProviderHealth(
                healthy=True,
                latency_ms=round(latency, 1),
                models_available=self.supported_models,
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return ProviderHealth(healthy=False, latency_ms=round(latency, 1), error=str(e))

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost in USD. Override per provider."""
        return 0.0

    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming."""
        return True

    def supports_embeddings(self) -> bool:
        """Whether this provider supports embeddings."""
        return False
