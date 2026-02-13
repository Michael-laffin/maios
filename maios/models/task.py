"""Task model for MAIOS."""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class TaskStatus(str, enum.Enum):
    """Status of a task."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Priority level of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(SQLModel, table=True):
    """Task model representing a unit of work in the system."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=10000)
    project_id: UUID = Field(..., foreign_key="project.id")
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    dependencies: list[UUID] = Field(default_factory=list, sa_column=Column(JSON))
    assigned_agent_id: Optional[UUID] = Field(default=None, foreign_key="agent.id")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    progress_percent: int = Field(default=0, ge=0, le=100)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    timeout_minutes: int = Field(default=30, ge=1, le=1440)  # Max 24 hours
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_count: int = Field(default=0, ge=0)
    result: Optional[str] = Field(default=None, max_length=50000)
    error_message: Optional[str] = Field(default=None, max_length=5000)
    skill_requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    complexity: str = Field(default="medium", max_length=20)
    task_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.update_timestamp()

    def complete(self, result: Optional[str] = None) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percent = 100
        if result:
            self.result = result
        self.update_timestamp()

    def fail(self, error_message: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.update_timestamp()

    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.update_timestamp()

    def block(self) -> None:
        """Mark task as blocked."""
        self.status = TaskStatus.BLOCKED
        self.update_timestamp()

    def unblock(self) -> None:
        """Unblock the task and return to pending."""
        self.status = TaskStatus.PENDING
        self.update_timestamp()

    def assign(self, agent_id: UUID) -> None:
        """Assign the task to an agent."""
        self.assigned_agent_id = agent_id
        self.status = TaskStatus.ASSIGNED
        self.update_timestamp()

    def unassign(self) -> None:
        """Unassign the task from its current agent."""
        self.assigned_agent_id = None
        self.status = TaskStatus.PENDING
        self.update_timestamp()

    def can_retry(self) -> bool:
        """Check if the task can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment the retry count."""
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.update_timestamp()

    def set_progress(self, percent: int) -> None:
        """Set the progress percentage."""
        self.progress_percent = max(0, min(100, percent))
        self.update_timestamp()

    def is_blocking(self, other_task_id: UUID) -> bool:
        """Check if this task is blocking another task."""
        return other_task_id in self.dependencies

    def add_dependency(self, task_id: UUID) -> None:
        """Add a dependency to this task."""
        if task_id not in self.dependencies and task_id != self.id:
            self.dependencies.append(task_id)
            self.update_timestamp()

    def remove_dependency(self, task_id: UUID) -> None:
        """Remove a dependency from this task."""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.update_timestamp()

    def is_expired(self) -> bool:
        """Check if the task has exceeded its timeout."""
        if self.started_at is None:
            return False
        elapsed = datetime.utcnow() - self.started_at
        return elapsed.total_seconds() > self.timeout_minutes * 60

    def is_subtask(self) -> bool:
        """Check if this task is a subtask of another task."""
        return self.parent_task_id is not None
