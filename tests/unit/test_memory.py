"""Tests for MemoryService."""

from typing import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from maios.models.memory import MemoryEntry, MemoryType


@pytest.fixture
async def memory_session() -> AsyncGenerator[AsyncSession, None]:
    """Create an in-memory SQLite database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create only the memoryentry table using raw SQL
    # We don't use SQLModel.metadata.create_all because other models have
    # FK constraints that would fail (no team, organization, user tables)
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS memoryentry (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                agent_id TEXT,
                project_id TEXT,
                task_id TEXT,
                team_id TEXT,
                embedding TEXT,
                importance REAL NOT NULL DEFAULT 0.5,
                access_count INTEGER NOT NULL DEFAULT 0,
                last_accessed TEXT,
                keywords TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        """))

    # Create session factory
    session_factory = async_sessionmaker(
        engine,
        class_=SQLModelAsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    # Cleanup
    await engine.dispose()


class TestMemoryServiceStore:
    """Tests for MemoryService.store method."""

    @pytest.mark.asyncio
    async def test_store_basic_memory(self, memory_session: AsyncSession):
        """Test storing a basic memory entry."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        memory = await service.store(
            content="Test memory content",
        )

        assert memory.id is not None
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.importance == 0.5
        assert memory.access_count == 0
        assert memory.keywords == []
        assert memory.tags == []

    @pytest.mark.asyncio
    async def test_store_memory_with_all_fields(self, memory_session: AsyncSession):
        """Test storing a memory with all optional fields."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent_id = uuid4()
        project_id = uuid4()
        task_id = uuid4()
        team_id = uuid4()

        memory = await service.store(
            content="Complete memory",
            memory_type=MemoryType.SEMANTIC,
            agent_id=agent_id,
            project_id=project_id,
            task_id=task_id,
            team_id=team_id,
            importance=0.8,
            keywords=["python", "test"],
            tags=["important", "unit-test"],
        )

        assert memory.content == "Complete memory"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.agent_id == agent_id
        assert memory.project_id == project_id
        assert memory.task_id == task_id
        assert memory.team_id == team_id
        assert memory.importance == 0.8
        assert memory.keywords == ["python", "test"]
        assert memory.tags == ["important", "unit-test"]

    @pytest.mark.asyncio
    async def test_store_memory_with_different_types(self, memory_session: AsyncSession):
        """Test storing memories with different memory types."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)

        episodic = await service.store("Episodic memory", memory_type=MemoryType.EPISODIC)
        assert episodic.memory_type == MemoryType.EPISODIC

        semantic = await service.store("Semantic memory", memory_type=MemoryType.SEMANTIC)
        assert semantic.memory_type == MemoryType.SEMANTIC

        procedural = await service.store("Procedural memory", memory_type=MemoryType.PROCEDURAL)
        assert procedural.memory_type == MemoryType.PROCEDURAL

        working = await service.store("Working memory", memory_type=MemoryType.WORKING)
        assert working.memory_type == MemoryType.WORKING


class TestMemoryServiceGet:
    """Tests for MemoryService.get method."""

    @pytest.mark.asyncio
    async def test_get_existing_memory(self, memory_session: AsyncSession):
        """Test getting an existing memory by ID."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        stored = await service.store("Memory to retrieve")

        retrieved = await service.get(stored.id)

        assert retrieved is not None
        assert retrieved.id == stored.id
        assert retrieved.content == "Memory to retrieve"

    @pytest.mark.asyncio
    async def test_get_nonexistent_memory(self, memory_session: AsyncSession):
        """Test getting a memory that doesn't exist."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        fake_id = uuid4()

        result = await service.get(fake_id)

        assert result is None


class TestMemoryServiceSearch:
    """Tests for MemoryService.search method."""

    @pytest.mark.asyncio
    async def test_search_by_content_keyword(self, memory_session: AsyncSession):
        """Test searching memories by content keyword."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Python is a programming language")
        await service.store("JavaScript is also popular")
        await service.store("Python has great libraries")

        results = await service.search("Python")

        assert len(results) == 2
        contents = [r.content for r in results]
        assert "Python is a programming language" in contents
        assert "Python has great libraries" in contents
        assert "JavaScript is also popular" not in contents

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, memory_session: AsyncSession):
        """Test that search is case insensitive."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Python Programming")

        results = await service.search("python")

        assert len(results) == 1
        assert results[0].content == "Python Programming"

    @pytest.mark.asyncio
    async def test_search_with_agent_filter(self, memory_session: AsyncSession):
        """Test searching with agent_id filter."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent1 = uuid4()
        agent2 = uuid4()

        await service.store("Agent 1 memory", agent_id=agent1)
        await service.store("Agent 2 memory", agent_id=agent2)
        await service.store("Agent 1 another", agent_id=agent1)

        results = await service.search("Agent", agent_id=agent1)

        assert len(results) == 2
        for r in results:
            assert r.agent_id == agent1

    @pytest.mark.asyncio
    async def test_search_with_project_filter(self, memory_session: AsyncSession):
        """Test searching with project_id filter."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        project1 = uuid4()
        project2 = uuid4()

        await service.store("Project 1 task", project_id=project1)
        await service.store("Project 2 task", project_id=project2)

        results = await service.search("task", project_id=project1)

        assert len(results) == 1
        assert results[0].project_id == project1

    @pytest.mark.asyncio
    async def test_search_with_memory_type_filter(self, memory_session: AsyncSession):
        """Test searching with memory_type filter."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)

        await service.store("Important fact", memory_type=MemoryType.SEMANTIC)
        await service.store("Important event", memory_type=MemoryType.EPISODIC)

        results = await service.search("Important", memory_type=MemoryType.SEMANTIC)

        assert len(results) == 1
        assert results[0].memory_type == MemoryType.SEMANTIC

    @pytest.mark.asyncio
    async def test_search_with_limit(self, memory_session: AsyncSession):
        """Test search with limit parameter."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)

        for i in range(5):
            await service.store(f"Test memory {i}")

        results = await service.search("Test", limit=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_no_results(self, memory_session: AsyncSession):
        """Test search that returns no results."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Some content")

        results = await service.search("nonexistent")

        assert len(results) == 0


class TestMemoryServiceGetByTags:
    """Tests for MemoryService.get_by_tags method."""

    @pytest.mark.asyncio
    async def test_get_by_tags_single_match(self, memory_session: AsyncSession):
        """Test getting memories by a single tag."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Important note", tags=["important"])
        await service.store("Regular note", tags=["normal"])

        results = await service.get_by_tags(["important"])

        assert len(results) == 1
        assert results[0].content == "Important note"

    @pytest.mark.asyncio
    async def test_get_by_tags_multiple_tags_match_any(self, memory_session: AsyncSession):
        """Test getting memories that match any of the tags."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Note 1", tags=["important"])
        await service.store("Note 2", tags=["urgent"])
        await service.store("Note 3", tags=["normal"])

        results = await service.get_by_tags(["important", "urgent"], match_all=False)

        assert len(results) == 2
        contents = [r.content for r in results]
        assert "Note 1" in contents
        assert "Note 2" in contents

    @pytest.mark.asyncio
    async def test_get_by_tags_multiple_tags_match_all(self, memory_session: AsyncSession):
        """Test getting memories that match all tags."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("Note 1", tags=["important", "urgent"])
        await service.store("Note 2", tags=["important"])
        await service.store("Note 3", tags=["urgent"])

        results = await service.get_by_tags(["important", "urgent"], match_all=True)

        assert len(results) == 1
        assert results[0].content == "Note 1"

    @pytest.mark.asyncio
    async def test_get_by_tags_with_agent_filter(self, memory_session: AsyncSession):
        """Test getting memories by tags with agent filter."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent1 = uuid4()
        agent2 = uuid4()

        await service.store("Agent 1 important", agent_id=agent1, tags=["important"])
        await service.store("Agent 2 important", agent_id=agent2, tags=["important"])

        results = await service.get_by_tags(["important"], agent_id=agent1)

        assert len(results) == 1
        assert results[0].agent_id == agent1

    @pytest.mark.asyncio
    async def test_get_by_tags_with_limit(self, memory_session: AsyncSession):
        """Test getting memories by tags with limit."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        for i in range(5):
            await service.store(f"Note {i}", tags=["important"])

        results = await service.get_by_tags(["important"], limit=3)

        assert len(results) == 3


class TestMemoryServiceGetRecent:
    """Tests for MemoryService.get_recent method."""

    @pytest.mark.asyncio
    async def test_get_recent_memories(self, memory_session: AsyncSession):
        """Test getting recent memories."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        await service.store("First memory")
        await service.store("Second memory")
        await service.store("Third memory")

        results = await service.get_recent()

        assert len(results) == 3
        # Most recent should be first
        assert results[0].content == "Third memory"

    @pytest.mark.asyncio
    async def test_get_recent_with_agent_filter(self, memory_session: AsyncSession):
        """Test getting recent memories for a specific agent."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent1 = uuid4()
        agent2 = uuid4()

        await service.store("Agent 1 memory", agent_id=agent1)
        await service.store("Agent 2 memory", agent_id=agent2)

        results = await service.get_recent(agent_id=agent1)

        assert len(results) == 1
        assert results[0].agent_id == agent1

    @pytest.mark.asyncio
    async def test_get_recent_with_project_filter(self, memory_session: AsyncSession):
        """Test getting recent memories for a specific project."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        project1 = uuid4()
        project2 = uuid4()

        await service.store("Project 1 memory", project_id=project1)
        await service.store("Project 2 memory", project_id=project2)

        results = await service.get_recent(project_id=project1)

        assert len(results) == 1
        assert results[0].project_id == project1

    @pytest.mark.asyncio
    async def test_get_recent_with_memory_type_filter(self, memory_session: AsyncSession):
        """Test getting recent memories of a specific type."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)

        await service.store("Semantic memory", memory_type=MemoryType.SEMANTIC)
        await service.store("Episodic memory", memory_type=MemoryType.EPISODIC)

        results = await service.get_recent(memory_type=MemoryType.SEMANTIC)

        assert len(results) == 1
        assert results[0].memory_type == MemoryType.SEMANTIC

    @pytest.mark.asyncio
    async def test_get_recent_with_limit(self, memory_session: AsyncSession):
        """Test getting recent memories with limit."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        for i in range(10):
            await service.store(f"Memory {i}")

        results = await service.get_recent(limit=5)

        assert len(results) == 5


class TestMemoryServiceAccess:
    """Tests for MemoryService.access method."""

    @pytest.mark.asyncio
    async def test_access_increments_count(self, memory_session: AsyncSession):
        """Test that access increments the access count."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        memory = await service.store("Test memory")

        result = await service.access(memory.id)

        assert result is True

        # Verify the access count was incremented
        updated = await service.get(memory.id)
        assert updated is not None
        assert updated.access_count == 1
        assert updated.last_accessed is not None

    @pytest.mark.asyncio
    async def test_access_multiple_times(self, memory_session: AsyncSession):
        """Test accessing memory multiple times."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        memory = await service.store("Test memory")

        await service.access(memory.id)
        await service.access(memory.id)
        await service.access(memory.id)

        updated = await service.get(memory.id)
        assert updated is not None
        assert updated.access_count == 3

    @pytest.mark.asyncio
    async def test_access_nonexistent_memory(self, memory_session: AsyncSession):
        """Test accessing a memory that doesn't exist."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        fake_id = uuid4()

        result = await service.access(fake_id)

        assert result is False


class TestMemoryServiceDelete:
    """Tests for MemoryService.delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_memory(self, memory_session: AsyncSession):
        """Test deleting an existing memory."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        memory = await service.store("Memory to delete")

        result = await service.delete(memory.id)

        assert result is True

        # Verify it was deleted
        deleted = await service.get(memory.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memory(self, memory_session: AsyncSession):
        """Test deleting a memory that doesn't exist."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        fake_id = uuid4()

        result = await service.delete(fake_id)

        assert result is False


class TestMemoryServiceSetEmbedding:
    """Tests for MemoryService.set_embedding method."""

    @pytest.mark.asyncio
    async def test_set_embedding(self, memory_session: AsyncSession):
        """Test setting the embedding for a memory."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        memory = await service.store("Test memory")

        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = await service.set_embedding(memory.id, embedding)

        assert result is True

        updated = await service.get(memory.id)
        assert updated is not None
        assert updated.embedding == embedding

    @pytest.mark.asyncio
    async def test_set_embedding_nonexistent_memory(self, memory_session: AsyncSession):
        """Test setting embedding for a nonexistent memory."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        fake_id = uuid4()

        result = await service.set_embedding(fake_id, [0.1, 0.2])

        assert result is False


class TestMemoryServiceGetByAgent:
    """Tests for MemoryService.get_by_agent method."""

    @pytest.mark.asyncio
    async def test_get_by_agent(self, memory_session: AsyncSession):
        """Test getting all memories for an agent."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent1 = uuid4()
        agent2 = uuid4()

        await service.store("Agent 1 memory 1", agent_id=agent1)
        await service.store("Agent 1 memory 2", agent_id=agent1)
        await service.store("Agent 2 memory", agent_id=agent2)

        results = await service.get_by_agent(agent1)

        assert len(results) == 2
        for r in results:
            assert r.agent_id == agent1

    @pytest.mark.asyncio
    async def test_get_by_agent_with_limit(self, memory_session: AsyncSession):
        """Test getting agent memories with limit."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent_id = uuid4()

        for i in range(10):
            await service.store(f"Memory {i}", agent_id=agent_id)

        results = await service.get_by_agent(agent_id, limit=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_get_by_agent_no_memories(self, memory_session: AsyncSession):
        """Test getting memories for an agent with no memories."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent_id = uuid4()

        results = await service.get_by_agent(agent_id)

        assert len(results) == 0


class TestMemoryServiceGetByProject:
    """Tests for MemoryService.get_by_project method."""

    @pytest.mark.asyncio
    async def test_get_by_project(self, memory_session: AsyncSession):
        """Test getting all memories for a project."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        project1 = uuid4()
        project2 = uuid4()

        await service.store("Project 1 memory 1", project_id=project1)
        await service.store("Project 1 memory 2", project_id=project1)
        await service.store("Project 2 memory", project_id=project2)

        results = await service.get_by_project(project1)

        assert len(results) == 2
        for r in results:
            assert r.project_id == project1

    @pytest.mark.asyncio
    async def test_get_by_project_with_limit(self, memory_session: AsyncSession):
        """Test getting project memories with limit."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        project_id = uuid4()

        for i in range(10):
            await service.store(f"Memory {i}", project_id=project_id)

        results = await service.get_by_project(project_id, limit=5)

        assert len(results) == 5


class TestMemoryServiceClearWorkingMemory:
    """Tests for MemoryService.clear_working_memory method."""

    @pytest.mark.asyncio
    async def test_clear_working_memory(self, memory_session: AsyncSession):
        """Test clearing working memory for an agent."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent_id = uuid4()

        await service.store("Working memory 1", agent_id=agent_id, memory_type=MemoryType.WORKING)
        await service.store("Working memory 2", agent_id=agent_id, memory_type=MemoryType.WORKING)
        await service.store("Episodic memory", agent_id=agent_id, memory_type=MemoryType.EPISODIC)

        count = await service.clear_working_memory(agent_id)

        assert count == 2

        # Verify working memories were deleted
        results = await service.get_by_agent(agent_id)
        assert len(results) == 1
        assert results[0].memory_type == MemoryType.EPISODIC

    @pytest.mark.asyncio
    async def test_clear_working_memory_no_memories(self, memory_session: AsyncSession):
        """Test clearing working memory when there are none."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent_id = uuid4()

        count = await service.clear_working_memory(agent_id)

        assert count == 0

    @pytest.mark.asyncio
    async def test_clear_working_memory_only_for_agent(self, memory_session: AsyncSession):
        """Test that clearing working memory only affects the specified agent."""
        from maios.core.memory.service import MemoryService

        service = MemoryService(memory_session)
        agent1 = uuid4()
        agent2 = uuid4()

        await service.store("Agent 1 working", agent_id=agent1, memory_type=MemoryType.WORKING)
        await service.store("Agent 2 working", agent_id=agent2, memory_type=MemoryType.WORKING)

        count = await service.clear_working_memory(agent1)

        assert count == 1

        # Verify only agent1's working memory was deleted
        agent1_memories = await service.get_by_agent(agent1)
        agent2_memories = await service.get_by_agent(agent2)

        assert len(agent1_memories) == 0
        assert len(agent2_memories) == 1
