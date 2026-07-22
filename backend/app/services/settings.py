"""Settings service — reads, validates, and writes user settings.

Settings are stored in a JSON file in the user's data directory.
Sensitive fields (API keys) are handled separately via keyring.
"""

from __future__ import annotations

import json
import structlog
from pathlib import Path
from typing import Any

from app.config.settings import settings

logger = structlog.get_logger("careerforge.settings")

_user_settings_path: Path | None = None


def _get_settings_path() -> Path:
    """Return the path to the user settings file."""
    global _user_settings_path
    if _user_settings_path is None:
        _user_settings_path = settings.resolved_data_dir / "settings.json"
    return _user_settings_path


def load_user_settings() -> dict[str, Any]:
    """Load user settings from disk, falling back to defaults."""
    path = _get_settings_path()
    defaults_path = Path(__file__).parent.parent.parent.parent / "config" / "default.json"

    defaults = {}
    if defaults_path.exists():
        defaults = json.loads(defaults_path.read_text(encoding="utf-8"))

    user = {}
    if path.exists():
        try:
            user = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("settings.load.corrupt", path=str(path))

    return _deep_merge(defaults, user)


def save_user_settings(settings_data: dict[str, Any]) -> None:
    """Persist user settings to disk atomically."""
    path = _get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write: write to temp, then rename
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(settings_data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(path)
    logger.info("settings.saved", path=str(path))


def update_setting(key: str, value: Any) -> dict[str, Any]:
    """Update a single setting by dot-notation key (e.g. 'ai.provider')."""
    current = load_user_settings()
    keys = key.split(".")
    target = current
    for k in keys[:-1]:
        target = target.setdefault(k, {})
    target[keys[-1]] = value
    save_user_settings(current)
    return current


def get_setting(key: str, default: Any = None) -> Any:
    """Get a single setting by dot-notation key."""
    settings_data = load_user_settings()
    keys = key.split(".")
    target = settings_data
    for k in keys:
        if isinstance(target, dict):
            target = target.get(k)
        else:
            return default
        if target is None:
            return default
    return target


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
