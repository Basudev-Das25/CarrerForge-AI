"""SQLAlchemy async engine and session factory.

Supports runtime engine override for testing — when TEST_DATABASE_URL
is set, it uses that instead of the configured URL.
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings

# Allow test override via environment variable
_test_database_url = os.environ.get("TEST_DATABASE_URL", "")


def _get_database_url() -> str:
    if _test_database_url:
        return _test_database_url
    # Resolve relative paths to absolute
    url = settings.database_url
    if url.startswith("sqlite+aiosqlite:///"):
        path_part = url.removeprefix("sqlite+aiosqlite:///")
        if not Path(path_part).is_absolute():
            # Resolve relative to the project root
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            abs_path = project_root / path_part
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{abs_path}"
    return url


engine = create_async_engine(
    _get_database_url(),
    echo=os.environ.get("DATABASE_ECHO", "").lower() in ("1", "true", "yes") or settings.database_echo,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async session with auto-commit.

    The session is committed on success and rolled back on exception.
    This is the standard FastAPI pattern for SQLAlchemy.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
