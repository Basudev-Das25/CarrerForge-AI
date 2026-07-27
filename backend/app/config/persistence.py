"""Config persistence — reads/writes AI provider settings to disk.

The onboarding wizard saves API keys here so the backend can access them.
Stored as JSON in the project config/ directory, loaded into settings
at startup, and used to auto-register providers into the orchestrator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.utils.logger import setup_logging

logger = setup_logging("careerforge.config")

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "ai_providers.json"

# Fields that get persisted
_PERSIST_KEYS = {
    "ai_provider",
    "openai_api_key", "openai_model",
    "anthropic_api_key", "anthropic_model",
    "openrouter_api_key", "openrouter_model",
    "grok_api_key", "grok_model",
    "huggingface_api_key",
    "ollama_base_url", "ollama_model",
}


def load_config() -> dict[str, Any]:
    """Load persisted AI provider config from disk."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("config.load.failed", error=str(exc))
    return {}


def save_config(data: dict[str, Any]) -> None:
    """Persist AI provider config to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Only save known keys
    filtered = {k: v for k, v in data.items() if k in _PERSIST_KEYS and v}
    existing = load_config()
    existing.update(filtered)
    CONFIG_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    logger.info("config.saved", keys=list(filtered.keys()))


def apply_config_to_settings() -> None:
    """Apply persisted config to the global settings singleton.

    Called at startup so settings.ai_provider, settings.openrouter_api_key, etc.
    reflect what the user saved during onboarding.
    """
    from app.config.settings import settings

    config = load_config()
    if not config:
        return

    # Get current values as base
    current = settings.model_dump()
    changed = False

    for key, value in config.items():
        if key in current and value:
            current[key] = value
            changed = True

    if not changed:
        return

    # model_construct skips env-var override (the root cause of BaseSettings
    # reverting to env values). We then copy fields onto the singleton.
    new_settings = settings.model_construct(**current)

    for field_name in new_settings.model_fields:
        val = getattr(new_settings, field_name)
        object.__setattr__(settings, field_name, val)

    logger.info("config.applied", provider=settings.ai_provider)


def register_providers_from_config(orchestrator: Any) -> None:
    """Auto-register AI providers into the orchestrator based on config.

    Called at startup after apply_config_to_settings().
    """
    from app.config.settings import settings
    from app.services.ai.providers.anthropic_provider import AnthropicProvider
    from app.services.ai.providers.grok_provider import GrokProvider
    from app.services.ai.providers.huggingface_provider import HuggingFaceProvider
    from app.services.ai.providers.ollama_provider import OllamaProvider
    from app.services.ai.providers.openai_provider import OpenAIProvider
    from app.services.ai.providers.openrouter_provider import OpenRouterProvider

    registered = []

    if settings.openai_api_key:
        orchestrator.register_provider(OpenAIProvider(api_key=settings.openai_api_key))
        registered.append("openai")

    if settings.anthropic_api_key:
        orchestrator.register_provider(AnthropicProvider(api_key=settings.anthropic_api_key))
        registered.append("anthropic")

    if settings.openrouter_api_key:
        orchestrator.register_provider(OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            default_model=settings.openrouter_model,
        ))
        registered.append("openrouter")

    if settings.grok_api_key:
        orchestrator.register_provider(GrokProvider(api_key=settings.grok_api_key))
        registered.append("grok")

    if settings.huggingface_api_key:
        orchestrator.register_provider(HuggingFaceProvider(api_key=settings.huggingface_api_key))
        registered.append("huggingface")

    # Ollama is always available (local, no key needed)
    orchestrator.register_provider(OllamaProvider(base_url=settings.ollama_base_url))
    registered.append("ollama")

    logger.info("providers.registered", providers=registered, default=settings.ai_provider)
