"""CareerForge AI — FastAPI Backend Entry Point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.db.base import Base, engine
from app.routers import (
    admin,
    agents_api,
    ai,
    ai_orchestrator,
    ats,
    ats_intelligence,
    backup,
    diagnostics,
    documents,
    jobs,
    keywords,
    knowledge,
    profile,
    resume_generator,
    resumes,
    updates,
)
from app.services.ai.orchestrator import orchestrator
from app.utils.logger import setup_logging

logger = setup_logging("careerforge")


def _register_providers() -> None:
    """Register AI providers based on available credentials.

    Checks environment variables / .env for API keys.
    Ollama is always registered because it requires no key.
    """
    from app.services.ai.providers.openai_provider import OpenAIProvider
    from app.services.ai.providers.anthropic_provider import AnthropicProvider
    from app.services.ai.providers.openrouter_provider import OpenRouterProvider
    from app.services.ai.providers.grok_provider import GrokProvider
    from app.services.ai.providers.huggingface_provider import HuggingFaceProvider
    from app.services.ai.providers.ollama_provider import OllamaProvider

    # Always register Ollama (local, no key needed)
    try:
        orchestrator.register_provider(OllamaProvider(base_url=settings.ollama_base_url))
    except Exception as exc:
        logger.warning("provider.register.failed", provider="ollama", error=str(exc))

    # Register cloud providers if credentials are available
    provider_configs: list[tuple[str, str, type]] = [
        ("openai", settings.openai_api_key, OpenAIProvider),
        ("anthropic", settings.anthropic_api_key, AnthropicProvider),
        ("openrouter", settings.openrouter_api_key, OpenRouterProvider),
        ("grok", settings.grok_api_key, GrokProvider),
        ("huggingface", settings.huggingface_api_key, HuggingFaceProvider),
    ]

    for name, api_key, provider_cls in provider_configs:
        if api_key:
            try:
                orchestrator.register_provider(provider_cls(api_key=api_key))
                logger.info("provider.registered", provider=name)
            except Exception as exc:
                logger.warning("provider.register.failed", provider=name, error=str(exc))
        else:
            logger.debug("provider.skipped", provider=name, reason="no API key")

    registered = list(orchestrator._providers.keys())
    logger.info("providers.available", count=len(registered), providers=registered)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Ensure data directories exist
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "documents").mkdir(exist_ok=True)
    (data_dir / "backups").mkdir(exist_ok=True)
    (Path(settings.lancedb_path)).mkdir(parents=True, exist_ok=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Register AI providers
    _register_providers()

    logger.info("careerforge.startup", data_dir=str(data_dir))
    yield
    logger.info("careerforge.shutdown")
    await engine.dispose()


# ── Security Headers ──────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


app = FastAPI(
    title="CareerForge AI",
    version="0.1.1",
    description="AI-powered desktop career intelligence platform",
    lifespan=lifespan,
)

# CORS — allow Tauri webview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420", "https://tauri.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)

# Routers
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
app.include_router(ats.router, prefix="/api/v1/ats", tags=["ats"])
app.include_router(profile.router, prefix="/api/v1", tags=["profile"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(ai_orchestrator.router, prefix="/api/v1/ai-orchestrator", tags=["ai-orchestrator"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(agents_api.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(resume_generator.router, prefix="/api/v1/resume", tags=["resume"])
app.include_router(ats_intelligence.router, prefix="/api/v1/ats-intelligence", tags=["ats-intelligence"])
app.include_router(updates.router, prefix="/api/v1/updates", tags=["updates"])
app.include_router(backup.router, prefix="/api/v1/backup", tags=["backup"])
app.include_router(diagnostics.router, prefix="/api/v1/diagnostics", tags=["diagnostics"])
app.include_router(keywords.router, prefix="/api/v1/keywords", tags=["keywords"])


@app.get("/")
async def root():
    return {"service": "CareerForge AI", "version": "0.1.1", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
