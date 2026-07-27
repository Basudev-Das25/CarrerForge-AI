"""Entry point used by the packaged desktop backend sidecar.

This intentionally starts Uvicorn in-process.  The installed desktop app
therefore does not depend on a system Python installation or on ``python``
being available on PATH.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="CareerForge AI backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Keep all mutable backend state out of Program Files and, for a
    # PyInstaller one-file build, out of its temporary extraction directory.
    app_data = Path(
        os.environ.get("CAREERFORGE_APP_DATA_DIR", Path.home() / ".careerforge")
    ).expanduser()
    app_data.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DATA_DIR", str(app_data))
    os.environ.setdefault(
        "DATABASE_URL", f"sqlite+aiosqlite:///{(app_data / 'careerforge.db').as_posix()}"
    )
    os.environ.setdefault("LANCEDB_PATH", str(app_data / "vector_store"))
    os.environ.setdefault("LOG_FILE", str(app_data / "logs" / "careerforge.log"))

    import uvicorn

    uvicorn.run("app.main:app", host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
