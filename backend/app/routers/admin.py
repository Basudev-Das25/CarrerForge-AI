"""Admin / health-check router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.base import get_db

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
