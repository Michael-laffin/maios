"""Agent model for MAIOS."""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class AgentStatus(str, enum.Enum):
    """Status of an agent."""

    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    DISABLED = "disabled"


class Agent(SQLModel, table=True):
    """Agent model representing an AI agent in the system."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    model_provider: str = Field(default="z.ai", max_length=100)
    model_name: str = Field(default="glm-4-plus", max_length=100)
    persona: str = Field(default="", max_length=2000)
    goals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    skill_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    permissions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    communication_access: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    system_prompt: Optional[str] = Field(default=None, max_length=10000)
    developer_prompt: Optional[str] = Field(default=None, max_length=10000)
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    performance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    tasks_completed: int = Field(default=0, ge=0)
    tasks_failed: int = Field(default=0, ge=0)
    current_task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    working_memory_limit: int = Field(default=10, ge=1, le=100)
    team_id: Optional[UUID] = Field(default=None)  # Team membership (Team model not yet implemented)
    is_active: bool = Field(default=True)
    last_heartbeat: Optional[datetime] = Field(default=None)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def record_heartbeat(self) -> None:
        """Record a heartbeat from this agent."""
        self.last_heartbeat = datetime.utcnow()
        self.update_timestamp()

    def mark_working(self, task_id: UUID) -> None:
        """Mark agent as working on a task."""
        self.status = AgentStatus.WORKING
        self.current_task_id = task_id
        self.update_timestamp()

    def mark_idle(self) -> None:
        """Mark agent as idle."""
        self.status = AgentStatus.IDLE
        self.current_task_id = None
        self.update_timestamp()

    def mark_error(self) -> None:
        """Mark agent as in error state."""
        self.status = AgentStatus.ERROR
        self.update_timestamp()

    def record_task_completion(self, success: bool = True) -> None:
        """Record a task completion."""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        # Update performance score
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.performance_score = self.tasks_completed / total_tasks
        self.update_timestamp()

    def can_communicate_with(self, other_agent_id: str) -> bool:
        """Check if this agent can communicate with another agent."""
        return (
            "*" in self.communication_access
            or other_agent_id in self.communication_access
        )

    def has_permission(self, permission: str) -> bool:
        """Check if this agent has a specific permission."""
        return "*" in self.permissions or permission in self.permissions

    def has_skill(self, skill: str) -> bool:
        """Check if this agent has a specific skill."""
        return skill in self.skill_tags
