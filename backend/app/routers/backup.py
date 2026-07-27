"""Backup API — create, restore, list, export, import, delete."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.backup.service import BackupService

router = APIRouter()


class BackupCreateRequest(BaseModel):
    description: str = ""


class BackupRestoreRequest(BaseModel):
    backup_id: str


class BackupExportRequest(BaseModel):
    backup_id: str
    export_path: str


class BackupImportRequest(BaseModel):
    import_path: str


@router.get("/")
async def list_backups():
    """List all available backups."""
    svc = BackupService()
    return svc.list_backups()


@router.post("/create")
async def create_backup(request: BackupCreateRequest):
    """Create a new backup."""
    svc = BackupService()
    meta = svc.create_backup(description=request.description)
    return {"backup": meta.to_dict()}


@router.post("/restore")
async def restore_backup(request: BackupRestoreRequest):
    """Restore a backup."""
    svc = BackupService()
    result = svc.restore_backup(request.backup_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/export")
async def export_backup(request: BackupExportRequest):
    """Export a backup to an external path."""
    svc = BackupService()
    result = svc.export_backup(request.backup_id, request.export_path)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/import")
async def import_backup(request: BackupImportRequest):
    """Import a backup from an external path."""
    svc = BackupService()
    meta = svc.import_backup(request.import_path)
    if not meta:
        raise HTTPException(status_code=400, detail="Invalid backup file")
    return {"backup": meta.to_dict()}


@router.delete("/{backup_id}")
async def delete_backup(backup_id: str):
    """Delete a backup."""
    svc = BackupService()
    svc.delete_backup(backup_id)
    return {"deleted": backup_id}
