"""Desktop Update Service — version management, update checking, and release metadata.

Isolates all update logic from the frontend. The Tauri updater handles
the actual download and installation via Rust commands. This service
provides release notes, version history, and update settings management.
"""

from __future__ import annotations

import json
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = structlog.get_logger("careerforge.update")


@dataclass
class UpdateChannel:
    """Configuration for an update channel."""
    name: str
    display_name: str
    description: str
    base_url: str


@dataclass
class ReleaseInfo:
    """Metadata about a release."""
    version: str
    published_date: str = ""
    release_notes: str = ""
    is_prerelease: bool = False
    download_url: str = ""
    checksum: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "published_date": self.published_date,
            "release_notes": self.release_notes,
            "is_prerelease": self.is_prerelease,
            "download_url": self.download_url,
        }


CHANNELS: list[UpdateChannel] = [
    UpdateChannel(
        name="stable",
        display_name="Stable",
        description="Most reliable releases, recommended for all users",
        base_url="https://github.com/Basudev-Das/CareerForge-AI/releases/latest",
    ),
    UpdateChannel(
        name="beta",
        display_name="Beta",
        description="Early access to features, may have minor issues",
        base_url="https://github.com/Basudev-Das/CareerForge-AI/releases",
    ),
    UpdateChannel(
        name="alpha",
        display_name="Alpha",
        description="Cutting edge, may be unstable",
        base_url="https://github.com/Basudev-Das/CareerForge-AI/releases",
    ),
]


# ── Update Settings ────────────────────────────────────────

DEFAULT_SETTINGS: dict[str, Any] = {
    "enabled": True,
    "check_on_startup": True,
    "check_interval": "weekly",  # daily, weekly, monthly
    "download_automatically": False,
    "install_automatically": False,
    "install_on_restart": True,
    "channel": "stable",
    "allow_metered_downloads": False,
    "skipped_versions": [],
    "last_check_date": None,
    "next_check_date": None,
}


class UpdateSettings:
    """Persistent update settings stored as JSON in the user's data directory."""

    def __init__(self, data_dir: str = ""):
        self._data_dir = Path(data_dir) if data_dir else Path.home() / ".careerforge"
        self._settings_file = self._data_dir / "update_settings.json"
        self._settings = dict(DEFAULT_SETTINGS)

    def load(self) -> dict[str, Any]:
        if self._settings_file.exists():
            try:
                data = json.loads(self._settings_file.read_text(encoding="utf-8"))
                self._settings = {**DEFAULT_SETTINGS, **data}
            except Exception:
                self._settings = dict(DEFAULT_SETTINGS)
        return dict(self._settings)

    def save(self, settings: dict[str, Any]) -> dict[str, Any]:
        self._settings = {**DEFAULT_SETTINGS, **settings}
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._settings_file.write_text(
            json.dumps(self._settings, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return dict(self._settings)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> dict[str, Any]:
        self._settings[key] = value
        return self.save(self._settings)

    def reset(self) -> dict[str, Any]:
        self._settings = dict(DEFAULT_SETTINGS)
        self.save(self._settings)
        return dict(self._settings)


# ── Update Service ─────────────────────────────────────────

class UpdateService:
    """Service for managing updates, release notes, and update history."""

    def __init__(self, data_dir: str = ""):
        self.settings = UpdateSettings(data_dir)
        self._data_dir = Path(data_dir) if data_dir else Path.home() / ".careerforge"
        self._history_file = self._data_dir / "update_history.json"

    # ── Channels ──────────────────────────────────────────

    @staticmethod
    def get_channels() -> list[dict[str, Any]]:
        return [
            {"name": c.name, "display_name": c.display_name,
             "description": c.description, "base_url": c.base_url}
            for c in CHANNELS
        ]

    # ── Settings ──────────────────────────────────────────

    def get_settings(self) -> dict[str, Any]:
        return self.settings.load()

    def update_settings(self, new_settings: dict[str, Any]) -> dict[str, Any]:
        return self.settings.save(new_settings)

    def reset_settings(self) -> dict[str, Any]:
        return self.settings.reset()

    # ── Version Info ──────────────────────────────────────

    @staticmethod
    def get_current_version() -> dict[str, Any]:
        return {
            "version": "0.1.1",
            "build_number": 1,
            "platform": "windows",
            "architecture": "x86_64",
            "published_date": "2026-07-22",
        }

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns -1, 0, or 1."""
        try:
            parts1 = [int(x) for x in v1.split(".")]
            parts2 = [int(x) for x in v2.split(".")]
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            for a, b in zip(parts1, parts2):
                if a < b:
                    return -1
                if a > b:
                    return 1
            return 0
        except (ValueError, AttributeError):
            return 0

    # ── Update History ────────────────────────────────────

    def get_history(self) -> dict[str, Any]:
        if not self._history_file.exists():
            return {"updates": [], "total": 0}

        try:
            data = json.loads(self._history_file.read_text(encoding="utf-8"))
            return data
        except Exception:
            return {"updates": [], "total": 0}

    def record_update(self, version: str, success: bool, error: str = "") -> dict[str, Any]:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        history = self.get_history()
        history["updates"].append({
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": success,
            "error": error,
        })
        history["total"] = len(history["updates"])

        # Keep last 50 entries
        if len(history["updates"]) > 50:
            history["updates"] = history["updates"][-50:]
            history["total"] = 50

        self._history_file.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return history

    # ── Release Notes ─────────────────────────────────────

    @staticmethod
    def get_release_notes() -> list[dict[str, Any]]:
        """Return the latest release highlights."""
        return [
            {"version": "0.1.0", "date": "2026-07-22", "type": "initial",
             "highlights": [
                 "Initial release of CareerForge AI",
                 "Candidate profile management with 12 entity types",
                 "Knowledge engine with semantic search",
                 "AI-powered resume generation pipeline",
                 "4 production-ready Typst resume templates",
                 "ATS intelligence with scoring and optimization",
                 "Multi-provider AI orchestration (OpenAI, Claude, Ollama)",
             ]},
        ]
