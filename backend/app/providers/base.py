"""Base provider interface — the contract all AI providers must implement."""

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
    usage: dict[str, int] = field(default_factory=dict)  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str = "stop"
    raw: dict[str, Any] | None = None


class AIProvider(ABC):
    """Abstract base class for all AI provider implementations.

    Every provider must implement `chat()`. Streaming and embedding
    are optional — providers that don't support them raise NotImplementedError.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name (e.g. 'OpenAI')."""

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """List of model identifiers this provider supports."""

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> ChatResponse:
        """Send a chat completion request and return the full response."""

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream chat completion tokens. Override if the provider supports it."""
        raise NotImplementedError(f"{self.name} does not support streaming")

    async def generate_embedding(self, text: str, model: str | None = None) -> list[float]:
        """Generate an embedding vector for the given text. Override if supported."""
        raise NotImplementedError(f"{self.name} does not support embeddings")

    async def health_check(self) -> bool:
        """Return True if the provider is reachable and configured correctly."""
        try:
            await self.chat(
                [ChatMessage(role=MessageRole.USER, content="ping")],
                max_tokens=5,
            )
            return True
        except Exception:
            return False
