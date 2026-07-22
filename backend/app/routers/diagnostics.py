"""Diagnostics API — system info, health checks, logs, export."""

from __future__ import annotations

from fastapi import APIRouter

from app.services.diagnostics.service import DiagnosticsService

router = APIRouter()


@router.get("/system")
async def get_system_info():
    """Get system information."""
    svc = DiagnosticsService()
    return svc.get_full_diagnostics()


@router.post("/health")
async def health_check():
    """Run health checks."""
    svc = DiagnosticsService()
    return await svc.health_check()


@router.get("/logs")
async def get_recent_logs(max_lines: int = 200):
    """Get recent log entries (redacted)."""
    svc = DiagnosticsService()
    return {"logs": svc.get_recent_logs(max_lines), "log_files": svc.get_log_paths()}


@router.post("/logs/clear")
async def clear_logs():
    """Clear all log files."""
    svc = DiagnosticsService()
    count = svc.clear_logs()
    return {"cleared": count}


@router.post("/export")
async def export_diagnostics():
    """Export system diagnostics to a zip file."""
    svc = DiagnosticsService()
    path = svc.export_diagnostics()
    return {"path": path, "message": "Diagnostics exported"}
