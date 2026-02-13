"""Memory model for MAIOS."""

import enum
import math
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class MemoryType(str, enum.Enum):
    """Type of memory entry."""

    EPISODIC = "episodic"  # Event-based memories
    SEMANTIC = "semantic"  # Fact-based memories
    PROCEDURAL = "procedural"  # Skill-based memories
    WORKING = "working"  # Short-term working memory


class MemoryEntry(SQLModel, table=True):
    """Memory entry model for storing agent memories."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str = Field(..., min_length=1, max_length=50000)
    memory_type: MemoryType = Field(default=MemoryType.EPISODIC)
    # Foreign keys are stored as UUIDs - FK constraints are enforced at DB level
    # This allows for easier testing with in-memory SQLite databases
    agent_id: Optional[UUID] = Field(default=None, index=True)
    project_id: Optional[UUID] = Field(default=None, index=True)
    task_id: Optional[UUID] = Field(default=None, index=True)
    team_id: Optional[UUID] = Field(default=None, index=True)
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(JSON))
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    access_count: int = Field(default=0, ge=0)
    last_accessed: Optional[datetime] = Field(default=None)
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    def access(self) -> None:
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)

    def set_importance(self, importance: float) -> None:
        """Set the importance score."""
        self.importance = max(0.0, min(1.0, importance))

    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to this memory."""
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)

    def remove_keyword(self, keyword: str) -> None:
        """Remove a keyword from this memory."""
        keyword = keyword.lower().strip()
        if keyword in self.keywords:
            self.keywords.remove(keyword)

    def add_tag(self, tag: str) -> None:
        """Add a tag to this memory."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this memory."""
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)

    def has_keyword(self, keyword: str) -> bool:
        """Check if this memory has a specific keyword."""
        return keyword.lower().strip() in self.keywords

    def has_tag(self, tag: str) -> bool:
        """Check if this memory has a specific tag."""
        return tag.lower().strip() in self.tags

    def set_embedding(self, embedding: list[float]) -> None:
        """Set the vector embedding for this memory."""
        self.embedding = embedding

    def has_embedding(self) -> bool:
        """Check if this memory has an embedding."""
        return self.embedding is not None and len(self.embedding) > 0

    def is_episodic(self) -> bool:
        """Check if this is an episodic memory."""
        return self.memory_type == MemoryType.EPISODIC

    def is_semantic(self) -> bool:
        """Check if this is a semantic memory."""
        return self.memory_type == MemoryType.SEMANTIC

    def is_procedural(self) -> bool:
        """Check if this is a procedural memory."""
        return self.memory_type == MemoryType.PROCEDURAL

    def is_working(self) -> bool:
        """Check if this is a working memory."""
        return self.memory_type == MemoryType.WORKING

    def get_relevance_score(self) -> float:
        """Calculate a relevance score based on access count and importance.

        Uses weighted combination:
        - 70% importance score
        - 30% access frequency (logarithmic scaling normalized by 10)
        """
        access_factor = math.log1p(self.access_count) / 10
        return min(1.0, self.importance * 0.7 + access_factor * 0.3)

    def is_related_to(
        self,
        agent_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
    ) -> bool:
        """Check if this memory is related to given entities."""
        if agent_id and self.agent_id == agent_id:
            return True
        if project_id and self.project_id == project_id:
            return True
        if task_id and self.task_id == task_id:
            return True
        if team_id and self.team_id == team_id:
            return True
        return False
