"""Integration tests for Backup API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_backups_empty(client):
    """Test listing backups when none exist."""
    response = await client.get("/api/v1/backup/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_backup(client):
    """Test creating a backup."""
    response = await client.post("/api/v1/backup/create", json={"description": "Test backup"})
    assert response.status_code == 200
    data = response.json()
    assert "backup" in data
    assert data["backup"]["description"] == "Test backup"


@pytest.mark.asyncio
async def test_restore_backup_not_found(client):
    """Test restoring a nonexistent backup."""
    response = await client.post("/api/v1/backup/restore", json={"backup_id": "nonexistent"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_backup(client):
    """Test deleting a backup."""
    # Create one first
    create_resp = await client.post("/api/v1/backup/create", json={"description": "To delete"})
    backup_id = create_resp.json()["backup"]["id"]

    # Delete it
    response = await client.delete(f"/api/v1/backup/{backup_id}")
    assert response.status_code == 200

    # Verify gone
    list_resp = await client.get("/api/v1/backup/")
    assert list_resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_diagnostics_system_info(client):
    """Test getting system diagnostics."""
    response = await client.get("/api/v1/diagnostics/system")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "providers" in data
    assert "templates" in data
    assert "data_dir" in data


@pytest.mark.asyncio
async def test_diagnostics_health_check(client):
    """Test health check endpoint."""
    response = await client.post("/api/v1/diagnostics/health")
    assert response.status_code == 200
    data = response.json()
    assert "data_dir" in data


@pytest.mark.asyncio
async def test_diagnostics_logs(client):
    """Test getting logs."""
    response = await client.get("/api/v1/diagnostics/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "log_files" in data
