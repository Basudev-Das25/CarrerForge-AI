"""Admin / health-check router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.config.persistence import load_config, save_config, apply_config_to_settings, register_providers_from_config
from app.db.base import get_db
from app.services.ai.orchestrator import orchestrator

router = APIRouter()


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


class AIProviderConfig(BaseModel):
    ai_provider: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    openrouter_api_key: str | None = None
    openrouter_model: str | None = None
    grok_api_key: str | None = None
    grok_model: str | None = None
    huggingface_api_key: str | None = None
    ollama_base_url: str | None = None
    ollama_model: str | None = None


@router.get("/config/ai")
async def get_ai_config():
    """Return persisted AI provider config (keys masked)."""
    config = load_config()
    # Mask API keys for security
    masked = {}
    for k, v in config.items():
        if "api_key" in k and v:
            masked[k] = v[:8] + "..." + v[-4:] if len(v) > 12 else "***"
        else:
            masked[k] = v
    return masked


@router.post("/config/ai")
async def save_ai_config(data: AIProviderConfig):
    """Save AI provider config and re-register providers."""
    save_config(data.model_dump(exclude_unset=True))
    apply_config_to_settings()
    register_providers_from_config(orchestrator)
    return {"status": "ok", "provider": settings.ai_provider}
