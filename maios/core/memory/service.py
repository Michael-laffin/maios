"""Memory service for managing agent memories."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from maios.models.memory import MemoryEntry, MemoryType


class MemoryService:
    """Service for managing agent memories."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        agent_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        importance: float = 0.5,
        keywords: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """Store a new memory entry."""
        memory = MemoryEntry(
            content=content,
            memory_type=memory_type,
            agent_id=agent_id,
            project_id=project_id,
            task_id=task_id,
            team_id=team_id,
            importance=importance,
            keywords=keywords or [],
            tags=tags or [],
        )
        self._session.add(memory)
        await self._session.flush()
        await self._session.refresh(memory)
        return memory

    async def get(self, memory_id: UUID) -> MemoryEntry | None:
        """Get a memory by ID."""
        result = await self._session.execute(
            select(MemoryEntry).where(MemoryEntry.id == memory_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        agent_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search memories by content (keyword match for now, semantic search later)."""
        # Escape SQL wildcard characters to prevent unintended pattern matching
        escaped_query = query.replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{escaped_query}%"

        stmt = select(MemoryEntry).where(
            MemoryEntry.content.ilike(search_pattern)
        )

        if agent_id is not None:
            stmt = stmt.where(MemoryEntry.agent_id == agent_id)

        if project_id is not None:
            stmt = stmt.where(MemoryEntry.project_id == project_id)

        if memory_type is not None:
            stmt = stmt.where(MemoryEntry.memory_type == memory_type)

        stmt = stmt.order_by(MemoryEntry.created_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tags(
        self,
        tags: list[str],
        agent_id: Optional[UUID] = None,
        match_all: bool = False,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Get memories matching tags."""
        if not tags:
            return []

        # Normalize tags to lowercase
        normalized_tags = [tag.lower().strip() for tag in tags]

        if match_all:
            # Need to match all tags - use JSON contains for each tag
            # SQLite uses json_each, PostgreSQL uses @> or &&
            # For SQLite compatibility, we fetch and filter in Python
            stmt = select(MemoryEntry)

            if agent_id is not None:
                stmt = stmt.where(MemoryEntry.agent_id == agent_id)

            result = await self._session.execute(stmt)
            memories = list(result.scalars().all())

            # Filter for memories that have ALL tags
            filtered = []
            for memory in memories:
                memory_tags_lower = [t.lower() for t in memory.tags]
                if all(tag in memory_tags_lower for tag in normalized_tags):
                    filtered.append(memory)

            return filtered[:limit]
        else:
            # Match ANY tag - can use JSON overlap in PostgreSQL
            # For SQLite compatibility, fetch and filter
            stmt = select(MemoryEntry)

            if agent_id is not None:
                stmt = stmt.where(MemoryEntry.agent_id == agent_id)

            result = await self._session.execute(stmt)
            memories = list(result.scalars().all())

            # Filter for memories that have ANY of the tags
            filtered = []
            for memory in memories:
                memory_tags_lower = [t.lower() for t in memory.tags]
                if any(tag in memory_tags_lower for tag in normalized_tags):
                    filtered.append(memory)

            # Sort by created_at descending
            filtered.sort(key=lambda m: m.created_at, reverse=True)
            return filtered[:limit]

    async def get_recent(
        self,
        agent_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Get recent memories."""
        stmt = select(MemoryEntry)

        if agent_id is not None:
            stmt = stmt.where(MemoryEntry.agent_id == agent_id)

        if project_id is not None:
            stmt = stmt.where(MemoryEntry.project_id == project_id)

        if memory_type is not None:
            stmt = stmt.where(MemoryEntry.memory_type == memory_type)

        stmt = stmt.order_by(MemoryEntry.created_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def access(self, memory_id: UUID) -> bool:
        """Mark a memory as accessed (increments access_count)."""
        memory = await self.get(memory_id)
        if memory is None:
            return False

        memory.access()
        await self._session.flush()
        return True

    async def delete(self, memory_id: UUID) -> bool:
        """Delete a memory."""
        result = await self._session.execute(
            delete(MemoryEntry).where(MemoryEntry.id == memory_id)
        )
        await self._session.flush()
        return result.rowcount > 0

    async def set_embedding(self, memory_id: UUID, embedding: list[float]) -> bool:
        """Set the vector embedding for a memory."""
        memory = await self.get(memory_id)
        if memory is None:
            return False

        memory.set_embedding(embedding)
        await self._session.flush()
        return True

    async def get_by_agent(self, agent_id: UUID, limit: int = 50) -> list[MemoryEntry]:
        """Get all memories for an agent."""
        stmt = (
            select(MemoryEntry)
            .where(MemoryEntry.agent_id == agent_id)
            .order_by(MemoryEntry.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project(self, project_id: UUID, limit: int = 50) -> list[MemoryEntry]:
        """Get all memories for a project."""
        stmt = (
            select(MemoryEntry)
            .where(MemoryEntry.project_id == project_id)
            .order_by(MemoryEntry.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def clear_working_memory(self, agent_id: UUID) -> int:
        """Clear working memory for an agent (delete all WORKING type memories)."""
        result = await self._session.execute(
            delete(MemoryEntry).where(
                MemoryEntry.agent_id == agent_id,
                MemoryEntry.memory_type == MemoryType.WORKING,
            )
        )
        await self._session.flush()
        return result.rowcount
