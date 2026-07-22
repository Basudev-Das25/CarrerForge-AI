"""Generic repository — abstracts common CRUD operations over SQLAlchemy async.

Supports soft delete, search, pagination, and filtering.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select, func, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class Repository(Generic[ModelType]):
    """Generic async CRUD repository with soft delete and search."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _apply_soft_delete_filter(self, query):
        """Filter out soft-deleted records if the model supports it."""
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))
        return query

    async def list(
        self,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ModelType]:
        """List records with optional filters, ordering, and pagination."""
        query = select(self.model)
        query = self._apply_soft_delete_filter(query)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)

        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_with_search(
        self,
        search: str | None = None,
        search_fields: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[Sequence[ModelType], int]:
        """List records with text search, returning items and total count."""
        query = select(self.model)
        query = self._apply_soft_delete_filter(query)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)

        # Text search across specified fields
        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    search_conditions.append(column.ilike(f"%{search}%"))
            if search_conditions:
                query = query.where(or_(*search_conditions))

        # Count total before pagination
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def get(self, id: str) -> ModelType | None:
        """Get a single record by primary key (excludes soft-deleted)."""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count records, optionally filtered (excludes soft-deleted)."""
        query = select(func.count()).select_from(self.model)
        query = self._apply_soft_delete_filter(query)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record from a dict."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: str, data: dict[str, Any]) -> ModelType | None:
        """Update a record by ID. Only non-None fields are updated. Increments version."""
        instance = await self.get(id)
        if instance is None:
            return None

        for key, value in data.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)

        # Increment version if model supports it
        if hasattr(instance, "version") and instance.version is not None:
            instance.version += 1

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: str) -> bool:
        """Soft-delete a record by setting deleted_at timestamp."""
        if not hasattr(self.model, "deleted_at"):
            return await self.delete(id)

        instance = await self.get(id)
        if instance is None:
            return False
        instance.deleted_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def delete(self, id: str) -> bool:
        """Hard-delete a record by ID. Returns True if deleted."""
        instance = await self.get(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def delete_all(self, filters: dict[str, Any] | None = None) -> int:
        """Delete multiple records. Returns count deleted."""
        query = delete(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.rowcount

    async def exists(self, id: str) -> bool:
        """Check if a record exists by ID (excludes soft-deleted)."""
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.scalar_one() > 0
