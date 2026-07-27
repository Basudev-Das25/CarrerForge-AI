"""Unit tests for the Update Service."""

import pytest

from app.services.update.service import (
    UpdateService, UpdateSettings, UpdateChannel,
    CHANNELS, DEFAULT_SETTINGS,
)


def test_compare_versions():
    assert UpdateService.compare_versions("0.1.0", "0.2.0") == -1
    assert UpdateService.compare_versions("0.2.0", "0.1.0") == 1
    assert UpdateService.compare_versions("0.1.0", "0.1.0") == 0
    assert UpdateService.compare_versions("1.0.0", "0.9.9") == 1
    assert UpdateService.compare_versions("0.1.0", "0.1.1") == -1
    assert UpdateService.compare_versions("10.20.30", "10.20.31") == -1
    assert UpdateService.compare_versions("2.0", "10.0") == -1
    assert UpdateService.compare_versions("abc", "def") == 0


def test_channels_exist():
    assert len(CHANNELS) >= 3
    names = [c.name for c in CHANNELS]
    assert "stable" in names
    assert "beta" in names
    assert "alpha" in names


def test_channel_properties():
    for ch in CHANNELS:
        assert ch.name
        assert ch.display_name
        assert ch.description
        assert ch.base_url.startswith("http")


def test_get_channels():
    result = UpdateService.get_channels()
    assert len(result) >= 3
    for ch in result:
        assert "name" in ch
        assert "display_name" in ch
        assert "description" in ch


def test_get_current_version():
    info = UpdateService.get_current_version()
    assert "version" in info
    assert "platform" in info
    assert info["platform"] == "windows"


def test_settings_defaults():
    svc = UpdateSettings()
    settings = svc.load()
    assert settings["enabled"] is True
    assert settings["check_on_startup"] is True
    assert settings["check_interval"] == "weekly"
    assert settings["channel"] == "stable"


def test_settings_save(tmp_path):
    settings_file = tmp_path / "update_settings.json"
    svc = UpdateSettings(data_dir=str(tmp_path))
    result = svc.save({"enabled": False, "channel": "beta"})
    assert result["enabled"] is False
    assert result["channel"] == "beta"
    assert settings_file.exists()


def test_settings_load_after_save(tmp_path):
    svc = UpdateSettings(data_dir=str(tmp_path))
    svc.save({"channel": "alpha"})
    svc2 = UpdateSettings(data_dir=str(tmp_path))
    loaded = svc2.load()
    assert loaded["channel"] == "alpha"
    # Other defaults should still be present
    assert loaded["enabled"] is True


def test_settings_reset(tmp_path):
    svc = UpdateSettings(data_dir=str(tmp_path))
    svc.save({"enabled": False, "channel": "alpha"})
    result = svc.reset()
    assert result["enabled"] is True
    assert result["channel"] == "stable"


def test_settings_get_set(tmp_path):
    svc = UpdateSettings(data_dir=str(tmp_path))
    svc.set("channel", "beta")
    assert svc.get("channel") == "beta"
    assert svc.get("nonexistent", "default") == "default"


def test_update_service_history(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    history = svc.get_history()
    assert history["total"] == 0
    assert history["updates"] == []


def test_update_service_record_update(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    history = svc.record_update("0.2.0", True)
    assert history["total"] == 1
    assert history["updates"][0]["version"] == "0.2.0"
    assert history["updates"][0]["success"] is True


def test_update_service_record_error(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    history = svc.record_update("0.3.0", False, error="Download failed")
    assert history["total"] == 1
    assert history["updates"][0]["success"] is False
    assert history["updates"][0]["error"] == "Download failed"


def test_update_history_limit(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    for i in range(60):
        svc.record_update(f"0.{i}.0", True)
    history = svc.get_history()
    assert history["total"] == 50  # Capped at 50


def test_release_notes():
    notes = UpdateService.get_release_notes()
    assert len(notes) >= 1
    for note in notes:
        assert "version" in note
        assert "highlights" in note
        assert len(note["highlights"]) >= 1


def test_default_settings_all_keys():
    expected_keys = [
        "enabled", "check_on_startup", "check_interval",
        "download_automatically", "install_automatically",
        "install_on_restart", "channel", "allow_metered_downloads",
        "skipped_versions", "last_check_date", "next_check_date",
    ]
    for key in expected_keys:
        assert key in DEFAULT_SETTINGS, f"Missing key: {key}"


def test_settings_get_update_service(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    settings = svc.get_settings()
    assert settings["enabled"] is True

    new_settings = svc.update_settings({"channel": "beta"})
    assert new_settings["channel"] == "beta"


def test_settings_reset_via_service(tmp_path):
    svc = UpdateService(data_dir=str(tmp_path))
    svc.update_settings({"channel": "alpha"})
    result = svc.reset_settings()
    assert result["channel"] == "stable"
    assert result["enabled"] is True
