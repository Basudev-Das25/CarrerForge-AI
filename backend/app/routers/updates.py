"""Update API — version management, settings, history, release notes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.update.service import UpdateService

router = APIRouter()


class UpdateSettingsRequest(BaseModel):
    enabled: bool = True
    check_on_startup: bool = True
    check_interval: str = "weekly"
    download_automatically: bool = False
    install_automatically: bool = False
    install_on_restart: bool = True
    channel: str = "stable"
    allow_metered_downloads: bool = False
    skipped_versions: list[str] = []


@router.get("/version")
async def get_current_version():
    """Get current application version info."""
    return UpdateService.get_current_version()


@router.get("/channels")
async def get_channels():
    """List available update channels."""
    return {"channels": UpdateService.get_channels()}


@router.get("/settings")
async def get_settings():
    """Get update settings."""
    svc = UpdateService()
    return svc.get_settings()


@router.put("/settings")
async def update_settings(request: UpdateSettingsRequest):
    """Update update settings."""
    svc = UpdateService()
    return svc.update_settings(request.model_dump())


@router.post("/settings/reset")
async def reset_settings():
    """Reset update settings to defaults."""
    svc = UpdateService()
    return svc.reset_settings()


@router.get("/history")
async def get_update_history():
    """Get update history."""
    svc = UpdateService()
    return svc.get_history()


@router.get("/release-notes")
async def get_release_notes():
    """Get release notes for the latest versions."""
    return {"releases": UpdateService.get_release_notes()}


@router.post("/history/record")
async def record_update(version: str, success: bool = True, error: str = ""):
    """Record an update in history (called by the Tauri updater)."""
    svc = UpdateService()
    return svc.record_update(version, success, error)
