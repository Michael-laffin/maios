"""Project model for MAIOS."""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class ProjectStatus(str, enum.Enum):
    """Status of a project."""

    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(SQLModel, table=True):
    """Project model representing a development project in the system."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)
    tech_stack: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    constraints: dict = Field(default_factory=dict, sa_column=Column(JSON))
    initial_request: Optional[str] = Field(default=None, max_length=10000)
    context_files: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    orchestrator_phase: str = Field(default="PLAN", max_length=50)
    project_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    organization_id: Optional[UUID] = Field(default=None)  # Organization membership (not yet implemented)
    owner_id: Optional[UUID] = Field(default=None)  # User ownership (not yet implemented)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the project."""
        self.status = ProjectStatus.ACTIVE
        self.update_timestamp()

    def pause(self) -> None:
        """Pause the project."""
        self.status = ProjectStatus.PAUSED
        self.update_timestamp()

    def complete(self) -> None:
        """Mark the project as completed."""
        self.status = ProjectStatus.COMPLETED
        self.update_timestamp()

    def cancel(self) -> None:
        """Cancel the project."""
        self.status = ProjectStatus.CANCELLED
        self.update_timestamp()

    def add_tech(self, technology: str) -> None:
        """Add a technology to the tech stack."""
        if technology not in self.tech_stack:
            self.tech_stack.append(technology)
            self.update_timestamp()

    def remove_tech(self, technology: str) -> None:
        """Remove a technology from the tech stack."""
        if technology in self.tech_stack:
            self.tech_stack.remove(technology)
            self.update_timestamp()

    def add_context_file(self, file_path: str) -> None:
        """Add a context file to the project."""
        if file_path not in self.context_files:
            self.context_files.append(file_path)
            self.update_timestamp()

    def remove_context_file(self, file_path: str) -> None:
        """Remove a context file from the project."""
        if file_path in self.context_files:
            self.context_files.remove(file_path)
            self.update_timestamp()

    def set_constraint(self, key: str, value: str | int | float | bool | list | dict) -> None:
        """Set a constraint for the project."""
        self.constraints[key] = value
        self.update_timestamp()

    def get_constraint(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a constraint value."""
        return self.constraints.get(key, default)

    def remove_constraint(self, key: str) -> None:
        """Remove a constraint from the project."""
        if key in self.constraints:
            del self.constraints[key]
            self.update_timestamp()

    def set_metadata(self, key: str, value: str | int | float | bool | list | dict) -> None:
        """Set a metadata value."""
        self.project_metadata[key] = value
        self.update_timestamp()

    def get_metadata(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a metadata value."""
        return self.project_metadata.get(key, default)

    def advance_phase(self, next_phase: str) -> None:
        """Advance to the next orchestrator phase."""
        self.orchestrator_phase = next_phase
        self.update_timestamp()

    def is_active(self) -> bool:
        """Check if the project is active."""
        return self.status == ProjectStatus.ACTIVE

    def is_editable(self) -> bool:
        """Check if the project can be edited."""
        return self.status in (ProjectStatus.PLANNING, ProjectStatus.ACTIVE, ProjectStatus.PAUSED)
