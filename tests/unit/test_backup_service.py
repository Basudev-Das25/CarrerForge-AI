"""Unit tests for the Backup Service."""

import pytest
from pathlib import Path

from app.services.backup.service import BackupService


def test_create_backup(tmp_path):
    svc = BackupService(data_dir=str(tmp_path))
    meta = svc.create_backup(description="Test backup")
    assert meta.id is not None
    assert meta.file_count >= 0
    assert meta.size_bytes > 0


def test_list_backups(tmp_path):
    svc = BackupService(data_dir=str(tmp_path))
    svc.create_backup("First")
    svc.create_backup("Second")
    result = svc.list_backups()
    assert result["total"] == 2


def test_delete_backup(tmp_path):
    svc = BackupService(data_dir=str(tmp_path))
    meta = svc.create_backup()
    svc.delete_backup(meta.id)
    result = svc.list_backups()
    assert result["total"] == 0


def test_restore_nonexistent(tmp_path):
    svc = BackupService(data_dir=str(tmp_path))
    result = svc.restore_backup("nonexistent")
    assert result["success"] is False


def test_multiple_backups(tmp_path):
    svc = BackupService(data_dir=str(tmp_path))
    for i in range(3):
        svc.create_backup(f"Backup {i}")
    result = svc.list_backups()
    assert result["total"] == 3
    backups = result["backups"]
    assert backups[2]["description"] == "Backup 2"
