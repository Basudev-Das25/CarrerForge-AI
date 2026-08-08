"""Diagnostics Service — system information, health checks, log management."""

from __future__ import annotations

import json
import os
import platform
import shutil
import structlog
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = structlog.get_logger("careerforge.diagnostics")


@dataclass
class SystemInfo:
    """System information for diagnostics."""
    version: str
    build_number: int
    os_name: str
    os_version: str
    cpu_info: str
    memory_gb: float
    python_version: str
    platform: str
    architecture: str
    backend_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version, "build_number": self.build_number,
            "os_name": self.os_name, "os_version": self.os_version,
            "cpu_info": self.cpu_info, "memory_gb": round(self.memory_gb, 1),
            "python_version": self.python_version, "platform": self.platform,
            "architecture": self.architecture, "backend_version": self.backend_version,
        }


class DiagnosticsService:
    """System diagnostics, health checks, and information."""

    REDACTED = "***REDACTED***"

    def __init__(self, data_dir: str = ""):
        self._data_dir = Path(data_dir) if data_dir else Path.home() / ".careerforge"
        self._logs_dir = self._data_dir / "logs"

    # ── System Info ───────────────────────────────────────

    def get_system_info(self) -> SystemInfo:
        """Collect system information."""
        return SystemInfo(
            version="0.1.1",
            build_number=1,
            os_name=platform.system(),
            os_version=platform.version(),
            cpu_info=platform.processor() or "Unknown",
            memory_gb=psutil_virtual_memory() if "psutil" in sys.modules else 0.0,
            python_version=sys.version.split()[0],
            platform=sys.platform,
            architecture=platform.machine(),
            backend_version="0.1.1",
        )

    def get_full_diagnostics(self) -> dict[str, Any]:
        """Collect complete diagnostics (excluding secrets)."""
        info = self.get_system_info()

        # Available providers (list only, no API keys)
        providers = []
        for env_name in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY",
                         "GROK_API_KEY", "HUGGINGFACE_API_KEY"]:
            providers.append({
                "name": env_name.removesuffix("_API_KEY").lower(),
                "configured": bool(os.environ.get(env_name, "")),
            })

        # Installed templates
        from app.services.templates.engine import TemplateEngine
        templates = [t.to_dict() for t in TemplateEngine.list_templates()]

        return {
            "system": info.to_dict(),
            "enabled_features": [
                "profile_management", "knowledge_engine", "ai_orchestration",
                "resume_generation", "template_engine", "ats_intelligence",
                "desktop_updates",
            ],
            "providers": providers,
            "templates": templates,
        }

    # ── Health Checks ─────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Run all health checks."""
        results = {}
        results["system"] = "ok"

        # Data directory
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            results["data_dir"] = "ok"
        except PermissionError:
            results["data_dir"] = "permission_denied"

        # Write test
        test_file = self._data_dir / ".health_test"
        try:
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            results["write_test"] = "ok"
        except Exception as e:
            results["write_test"] = f"failed: {e}"

        return results

    # ── Log Management ────────────────────────────────────

    def get_log_paths(self) -> list[str]:
        """Get paths to all log files."""
        if not self._logs_dir.exists():
            return []
        logs = []
        for f in sorted(self._logs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.suffix in (".log", ".txt", ".json") or f.name.startswith("careerforge"):
                logs.append(str(f))
        return logs[:10]

    def get_recent_logs(self, max_lines: int = 200) -> str:
        """Get the most recent log entries, redacting sensitive data."""
        log_files = self.get_log_paths()
        if not log_files:
            return "No log files found."

        lines = []
        for log_path in log_files[:3]:
            try:
                content = Path(log_path).read_text(encoding="utf-8", errors="ignore")
                file_lines = content.strip().split("\n")[-max_lines:]
                lines.append(f"=== {Path(log_path).name} ===\n")
                lines.extend(file_lines)
            except Exception:
                continue

        result = "\n".join(lines)
        result = self._redact_sensitive(result)
        return result

    def export_diagnostics(self, export_dir: str | None = None) -> str:
        """Export system diagnostics to a zip file."""
        if export_dir:
            export_path = Path(export_dir) / "careerforge_diagnostics.zip"
        else:
            export_path = self._data_dir / "careerforge_diagnostics.zip"

        export_path.parent.mkdir(parents=True, exist_ok=True)

        info = self.get_full_diagnostics()

        with zipfile.ZipFile(str(export_path), "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("diagnostics.json", json.dumps(info, indent=2))

            recent_logs = self.get_recent_logs(500)
            zf.writestr("recent_logs.txt", self._redact_sensitive(recent_logs))

        logger.info("diagnostics.exported", path=str(export_path))
        return str(export_path)

    def clear_logs(self) -> int:
        """Clear all log files. Returns count of deleted files."""
        count = 0
        for log_file in self.get_log_paths():
            try:
                Path(log_file).unlink()
                count += 1
            except Exception:
                pass
        return count

    # ── Redaction ─────────────────────────────────────────

    def _redact_sensitive(self, text: str) -> str:
        """Redact API keys and secrets from log content."""
        import re
        # API key patterns
        patterns = [
            r'(sk-[a-zA-Z0-9]{20,})',  # OpenAI
            r'(sk-ant-[a-zA-Z0-9]{20,})',  # Anthropic
            r'(api_key[=:]["\']?[a-zA-Z0-9_\-]{20,})',
            r'(API_KEY[=:]["\']?[a-zA-Z0-9_\-]{20,})',
            r'(Bearer\s+[a-zA-Z0-9_\-\.]{20,})',
        ]
        for pattern in patterns:
            text = re.sub(pattern, self.REDACTED, text)
        return text


def psutil_virtual_memory() -> float:
    """Get system memory in GB. Returns 0 if psutil not available."""
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        return 0.0
