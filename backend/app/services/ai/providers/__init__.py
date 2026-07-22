"""AI Provider Abstraction — unified interface for all AI providers.

Every provider exposes identical interfaces. The orchestrator
handles provider selection, failover, and caching.
"""

from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
    MessageRole,
    ProviderHealth,
)

__all__ = [
    "AIProvider",
    "ChatMessage",
    "ChatResponse",
    "EmbeddingResponse",
    "MessageRole",
    "ProviderHealth",
]
