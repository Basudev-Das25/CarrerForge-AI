"""Build the self-contained Python backend executable used by Tauri.

The output name includes Tauri's target-triple suffix because that is the
convention required by ``bundle.externalBin``.  Tauri removes the suffix when
it places the executable beside the installed application.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
BINARY_DIR = ROOT / "src-tauri" / "binaries"
BUILD_DIR = ROOT / ".backend-sidecar-build"
DIST_DIR = BUILD_DIR / "dist"


def target_triple() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "x86_64" if machine in {"amd64", "x86_64"} else machine
    if system == "windows":
        return f"{arch}-pc-windows-msvc"
    if system == "darwin":
        return f"{arch}-apple-darwin"
    return f"{arch}-unknown-linux-gnu"


def main() -> None:
    if not shutil.which("python") and sys.executable == "":
        raise RuntimeError("A Python interpreter is required to build the backend sidecar.")

    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "PyInstaller is missing. Run: backend\\.venv\\Scripts\\python.exe -m pip "
            "install -r backend\\requirements.txt"
        ) from exc

    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    BINARY_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "careerforge-backend",
        "--paths",
        str(BACKEND),
        # SQLAlchemy async SQLite driver (imported dynamically by sqlalchemy.dialects)
        "--hidden-import", "aiosqlite",
        # SQLAlchemy dialect modules (imported dynamically via entry points)
        "--hidden-import", "sqlalchemy.ext.asyncio",
        "--hidden-import", "sqlalchemy.dialects.sqlite.aiosqlite",
        # PyMuPDF (imported dynamically in document_processor)
        "--hidden-import", "fitz",
        # Core app modules
        "--hidden-import", "app.main",
        "--hidden-import", "app.config.settings",
        "--hidden-import", "app.config.persistence",
        "--hidden-import", "app.db.base",
        "--hidden-import", "app.services.ai.orchestrator",
        "--collect-submodules",
        "app",
        "--collect-submodules",
        "uvicorn",
        "--collect-all",
        "sentence_transformers",
        "--collect-all",
        "lancedb",
        "--collect-all",
        "uvicorn",
        "--collect-all",
        "aiosqlite",
        "--collect-all",
        "numpy",
        "--collect-all",
        "pyarrow",
        "--add-data",
        f"{BACKEND / 'templates'}{os.pathsep}templates",
        "--add-data",
        f"{BACKEND / 'prompts'}{os.pathsep}prompts",
        "--workpath",
        str(BUILD_DIR / "work"),
        "--distpath",
        str(DIST_DIR),
        "--specpath",
        str(BUILD_DIR / "spec"),
        str(BACKEND / "launcher.py"),
    ]
    # Some Windows installations contain a per-user site-packages directory
    # that is not readable by the current process. The sidecar must be built
    # only from the project's virtual environment, not from user-site Python.
    environment = os.environ.copy()
    environment["PYTHONNOUSERSITE"] = "1"
    # PyInstaller still probes site.getusersitepackages() while discovering
    # DLLs. Point APPDATA at the private build directory so an inaccessible
    # global user-site folder cannot abort a release build.
    appdata_dir = BUILD_DIR / "appdata"
    appdata_dir.mkdir(parents=True, exist_ok=True)
    environment["APPDATA"] = str(appdata_dir)
    subprocess.run(command, check=True, cwd=ROOT, env=environment)

    extension = ".exe" if os.name == "nt" else ""
    source = DIST_DIR / f"careerforge-backend{extension}"
    
    # Copy with target triple for Tauri externalBin with explicit path
    destination = BINARY_DIR / f"careerforge-backend-{target_triple()}{extension}"
    shutil.copy2(source, destination)
    
    # Also copy unsuffixed version for Tauri externalBin fallback
    unsuffixed = BINARY_DIR / f"careerforge-backend{extension}"
    shutil.copy2(source, unsuffixed)
    
    print(f"Built backend sidecar: {destination}")
    print(f"Also created unsuffixed version: {unsuffixed}")


if __name__ == "__main__":
    main()
