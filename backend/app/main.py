"""CareerForge AI — FastAPI Backend Entry Point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.db.base import Base, engine
from app.routers import (
    admin,
    agents_api,
    ai,
    ai_orchestrator,
    ats,
    documents,
    jobs,
    knowledge,
    profile,
    resumes,
)
from app.utils.logger import setup_logging

logger = setup_logging("careerforge")


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

    logger.info("careerforge.startup", data_dir=str(data_dir))
    yield
    logger.info("careerforge.shutdown")
    await engine.dispose()


app = FastAPI(
    title="CareerForge AI",
    version="0.1.0",
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


@app.get("/")
async def root():
    return {"service": "CareerForge AI", "version": "0.1.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
