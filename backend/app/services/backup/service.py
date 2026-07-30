"""Backup System — automatic backup, restore, export, and import."""

from __future__ import annotations

import json
import os
import shutil
import structlog
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = structlog.get_logger("careerforge.backup")


@dataclass
class BackupMetadata:
    """Metadata for a backup."""
    id: str = ""
    timestamp: str = ""
    version: str = ""
    size_bytes: int = 0
    file_count: int = 0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "timestamp": self.timestamp, "version": self.version,
            "size_bytes": self.size_bytes, "file_count": self.file_count,
            "description": self.description,
        }


def _safe_extract(zf: zipfile.ZipFile, member: str, target_dir: Path) -> Path:
    """Extract a zip member safely, preventing path traversal."""
    full_path = target_dir.resolve() / member
    full_path = full_path.resolve()
    if not str(full_path).startswith(str(target_dir.resolve())):
        raise ValueError(f"Zip slip detected: {member} resolves outside {target_dir}")
    zf.extract(member, target_dir)
    return full_path


class BackupService:
    """Automatic backup and restore system."""

    BACKUP_DIRS = ["config", "templates", "prompts"]
    BACKUP_FILES = ["update_settings.json", "settings.json"]

    def __init__(self, data_dir: str = ""):
        self._data_dir = Path(data_dir) if data_dir else Path.home() / ".careerforge"
        self._backups_dir = self._data_dir / "backups"
        self._backups_index = self._backups_dir / "index.json"

    # ── Create Backup ─────────────────────────────────────

    def create_backup(self, description: str = "") -> BackupMetadata:
        """Create a complete backup of user data."""
        self._backups_dir.mkdir(parents=True, exist_ok=True)
        backup_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        index = self._load_index()
        meta = BackupMetadata(
            id=backup_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="0.5.0-alpha",
            description=description or "Automatic backup",
        )

        # Create backup zip
        zip_path = self._backups_dir / f"backup_{backup_id}.zip"
        file_count = 0

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Backup settings files
            for fname in self.BACKUP_FILES:
                fpath = self._data_dir / fname
                if fpath.exists():
                    zf.write(fpath, f"settings/{fname}")
                    file_count += 1

            # Backup directories
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            for dirname in self.BACKUP_DIRS:
                src_dir = project_root / dirname
                if src_dir.exists():
                    for f in src_dir.rglob("*"):
                        if f.is_file() and not f.name.startswith("."):
                            arcname = f"project/{dirname}/{f.relative_to(src_dir)}"
                            zf.write(f, arcname)
                            file_count += 1

            # Backup database
            db_file = self._data_dir / "careerforge.db"
            if not db_file.exists():
                db_file = Path("data/careerforge.db")
            if db_file.exists():
                zf.write(db_file, "database/careerforge.db")
                file_count += 1

            # Write metadata inside zip
            zf.writestr("metadata.json", json.dumps({
                "id": backup_id, "timestamp": meta.timestamp,
                "version": meta.version, "description": meta.description,
            }, indent=2))

        meta.size_bytes = zip_path.stat().st_size
        meta.file_count = file_count

        # Update index
        index["backups"].append(meta.to_dict())
        index["total"] = len(index["backups"])
        self._save_index(index)

        logger.info("backup.created", id=backup_id, size=meta.size_bytes, files=file_count)
        return meta

    # ── Restore Backup ────────────────────────────────────

    def restore_backup(self, backup_id: str) -> dict[str, Any]:
        """Restore a backup from the backups directory."""
        zip_path = self._backups_dir / f"backup_{backup_id}.zip"
        if not zip_path.exists():
            return {"success": False, "error": f"Backup {backup_id} not found"}

        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        restored_files = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            # Validate all members before extraction
            for member in zf.namelist():
                if member == "metadata.json":
                    continue
                # Check for path traversal in member name
                resolved = Path(self._data_dir) / member
                resolved = resolved.resolve()
                if not str(resolved).startswith(str(self._data_dir.resolve())):
                    return {"success": False, "error": f"Invalid backup: path traversal detected in '{member}'"}

            for member in zf.namelist():
                if member == "metadata.json":
                    continue

                if member.startswith("settings/"):
                    filename = member.removeprefix("settings/")
                    dest = _safe_extract(zf, member, self._data_dir)
                    restored_files.append(str(dest))

                elif member.startswith("database/"):
                    dest = _safe_extract(zf, member, self._data_dir)
                    restored_files.append(str(self._data_dir / member.removeprefix("database/")))

                elif member.startswith("project/"):
                    parts = member.removeprefix("project/").split("/", 1)
                    if len(parts) == 2:
                        dirname, rel_path = parts
                        dest = project_root / dirname / rel_path
                        # Validate no path traversal
                        dest = dest.resolve()
                        if not str(dest).startswith(str(project_root.resolve())):
                            return {"success": False, "error": f"Invalid backup: path traversal detected in '{member}'"}
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        with open(dest, "wb") as f:
                            f.write(zf.read(member))
                        restored_files.append(str(dest))

        logger.info("backup.restored", id=backup_id, files=len(restored_files))
        return {"success": True, "restored_files": len(restored_files), "files": restored_files}

    # ── Export Backup ─────────────────────────────────────

    def export_backup(self, backup_id: str, export_path: str) -> dict[str, Any]:
        """Export a backup to an external path."""
        src = self._backups_dir / f"backup_{backup_id}.zip"
        if not src.exists():
            return {"success": False, "error": "Backup not found"}
        dest = Path(export_path).resolve()
        # Allow writing to user's home directory and common locations
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))
        return {"success": True, "path": str(dest)}

    # ── Import Backup ─────────────────────────────────────

    def import_backup(self, import_path: str) -> BackupMetadata | None:
        """Import a backup from an external path."""
        src = Path(import_path)
        if not src.exists() or not src.name.endswith(".zip"):
            return None

        # Validate it's a real zip file
        try:
            with zipfile.ZipFile(src, "r") as zf:
                if zf.testzip():
                    return None  # Corrupt zip
                # Check for path traversal in members
                for member in zf.namelist():
                    resolved = (Path(self._data_dir) / member).resolve()
                    if not str(resolved).startswith(str(self._data_dir.resolve())):
                        return None
        except (zipfile.BadZipFile, Exception):
            return None

        self._backups_dir.mkdir(parents=True, exist_ok=True)
        backup_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest = self._backups_dir / f"backup_{backup_id}.zip"
        shutil.copy2(str(src), str(dest))

        meta = BackupMetadata(
            id=backup_id, timestamp=datetime.now(timezone.utc).isoformat(),
            version="imported", size_bytes=dest.stat().st_size,
            description=f"Imported from {src.name}",
        )

        index = self._load_index()
        index["backups"].append(meta.to_dict())
        index["total"] = len(index["backups"])
        self._save_index(index)

        return meta

    # ── Delete Backup ─────────────────────────────────────

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a specific backup."""
        zip_path = self._backups_dir / f"backup_{backup_id}.zip"
        if zip_path.exists():
            zip_path.unlink()

        index = self._load_index()
        index["backups"] = [b for b in index["backups"] if b["id"] != backup_id]
        index["total"] = len(index["backups"])
        self._save_index(index)
        return True

    # ── List Backups ──────────────────────────────────────

    def list_backups(self) -> dict[str, Any]:
        """List all available backups."""
        return self._load_index()

    # ── Index Management ──────────────────────────────────

    def _load_index(self) -> dict:
        if self._backups_index.exists():
            try:
                return json.loads(self._backups_index.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"backups": [], "total": 0}

    def _save_index(self, data: dict) -> None:
        self._backups_dir.mkdir(parents=True, exist_ok=True)
        self._backups_index.write_text(json.dumps(data, indent=2), encoding="utf-8")
