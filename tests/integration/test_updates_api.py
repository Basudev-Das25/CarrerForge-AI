"""Integration tests for Update Settings API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_get_current_version(client):
    """Test getting the current version."""
    response = await client.get("/api/v1/updates/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "platform" in data


@pytest.mark.asyncio
async def test_get_channels(client):
    """Test listing update channels."""
    response = await client.get("/api/v1/updates/channels")
    assert response.status_code == 200
    data = response.json()
    assert "channels" in data
    assert len(data["channels"]) >= 1
    # Check stable channel exists
    names = {c["name"] for c in data["channels"]}
    assert "stable" in names


@pytest.mark.asyncio
async def test_get_settings(client):
    """Test getting default update settings."""
    response = await client.get("/api/v1/updates/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["channel"] == "stable"
    assert data["check_interval"] in ("daily", "weekly", "monthly")


@pytest.mark.asyncio
async def test_update_settings(client):
    """Test updating update settings."""
    response = await client.put(
        "/api/v1/updates/settings",
        json={"enabled": False, "channel": "beta", "check_interval": "daily"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["channel"] == "beta"


@pytest.mark.asyncio
async def test_reset_settings(client):
    """Test resetting update settings to defaults."""
    response = await client.post("/api/v1/updates/settings/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["channel"] == "stable"


@pytest.mark.asyncio
async def test_record_update(client):
    """Test recording an update in history."""
    response = await client.post(
        "/api/v1/updates/history/record",
        params={"version": "0.2.0", "success": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["updates"][0]["version"] == "0.2.0"
    assert data["updates"][0]["success"] is True


@pytest.mark.asyncio
async def test_get_release_notes(client):
    """Test getting release notes."""
    response = await client.get("/api/v1/updates/release-notes")
    assert response.status_code == 200
    data = response.json()
    assert "releases" in data
    assert len(data["releases"]) >= 1


@pytest.mark.asyncio
async def test_compare_versions():
    """Test version comparison utility."""
    from app.services.update.service import UpdateService
    assert UpdateService.compare_versions("0.1.0", "0.2.0") == -1
    assert UpdateService.compare_versions("0.2.0", "0.1.0") == 1
    assert UpdateService.compare_versions("0.1.0", "0.1.0") == 0
    assert UpdateService.compare_versions("1.0.0", "0.9.9") == 1
    assert UpdateService.compare_versions("0.1.0", "0.1.1") == -1
