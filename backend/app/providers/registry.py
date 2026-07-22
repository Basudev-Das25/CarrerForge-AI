"""Provider registry — discovers, caches, and returns the active provider."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.config.settings import settings

if TYPE_CHECKING:
    from app.providers.base import AIProvider

logger = logging.getLogger("careerforge.providers")

_registry: dict[str, type[AIProvider]] = {}
_instance: AIProvider | None = None


def register_provider(name: str, cls: type[AIProvider]) -> None:
    """Register a provider class by name."""
    _registry[name] = cls
    logger.debug("provider.registered", name=name)


def get_provider(name: str | None = None) -> AIProvider:
    """Return a singleton instance of the requested (or configured) provider.

    Provider is instantiated lazily on first call.
    """
    global _instance

    provider_name = (name or settings.ai_provider).lower()

    if _instance is not None and _instance.name.lower() == provider_name:
        return _instance

    if provider_name not in _registry:
        _auto_register()

    if provider_name not in _registry:
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Available: {list(_registry.keys())}"
        )

    cls = _registry[provider_name]
    _instance = cls()
    logger.info("provider.instantiated", name=provider_name)
    return _instance


def _auto_register() -> None:
    """Import all provider modules to trigger their self-registration."""
    # Each provider module calls `register_provider()` on import.
    try:
        from app.providers import openai_provider  # noqa: F401
    except ImportError:
        pass
    try:
        from app.providers import anthropic_provider  # noqa: F401
    except ImportError:
        pass
    try:
        from app.providers import openrouter_provider  # noqa: F401
    except ImportError:
        pass
    try:
        from app.providers import ollama_provider  # noqa: F401
    except ImportError:
        pass


def list_providers() -> list[dict]:
    """Return metadata about all registered providers."""
    _auto_register()
    result = []
    for name, cls in _registry.items():
        try:
            instance = cls()
            result.append({
                "name": instance.name,
                "id": name,
                "models": instance.supported_models,
            })
        except Exception:
            # Provider may need API key — still list it
            result.append({
                "name": name,
                "id": name,
                "models": [],
            })
    return result
