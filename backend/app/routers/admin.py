"""Admin / health-check / config router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.base import get_db
from app.services.ai.orchestrator import orchestrator

router = APIRouter()


class AiConfigRequest(BaseModel):
    ai_provider: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    grok_api_key: str = ""
    huggingface_api_key: str = ""
    model: str = ""


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "connected",
    }


@router.get("/config")
async def get_config():
    return {
        "ai_provider": settings.ai_provider,
        "embedding_model": settings.embedding_model,
        "debug": settings.debug,
    }


@router.post("/config/ai")
async def set_ai_config(request: AiConfigRequest):
    """Save AI provider config and register the provider at runtime."""
    from app.services.ai.providers.openai_provider import OpenAIProvider
    from app.services.ai.providers.anthropic_provider import AnthropicProvider
    from app.services.ai.providers.openrouter_provider import OpenRouterProvider
    from app.services.ai.providers.grok_provider import GrokProvider
    from app.services.ai.providers.huggingface_provider import HuggingFaceProvider

    provider = request.ai_provider
    api_key = ""
    provider_cls = None

    # Map provider name to its class and key
    provider_map: dict[str, tuple[str, type]] = {
        "openai": (request.openai_api_key or settings.openai_api_key, OpenAIProvider),
        "anthropic": (request.anthropic_api_key or settings.anthropic_api_key, AnthropicProvider),
        "openrouter": (request.openrouter_api_key or settings.openrouter_api_key, OpenRouterProvider),
        "grok": (request.grok_api_key or settings.grok_api_key, GrokProvider),
        "huggingface": (request.huggingface_api_key or settings.huggingface_api_key, HuggingFaceProvider),
        "ollama": ("", None),  # Always available, registered at startup
    }

    if provider not in provider_map:
        return {"status": "error", "message": f"Unknown provider: {provider}"}

    key, provider_cls = provider_map[provider]

    if provider_cls and key:
        try:
            orchestrator.register_provider(provider_cls(api_key=key))
            return {"status": "ok", "provider": provider}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    if provider == "ollama":
        return {"status": "ok", "provider": "ollama"}

    return {"status": "error", "message": f"No API key provided for {provider}"}
