"""Orchestrator state definitions."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrchestratorPhase(str, Enum):
    """Phases of the orchestrator state machine."""

    PLAN = "PLAN"
    DELEGATE = "DELEGATE"
    MONITOR = "MONITOR"
    ESCALATE = "ESCALATE"
    REASSIGN = "REASSIGN"
    COMPLETE = "COMPLETE"


class OrchestratorState(BaseModel):
    """State for the orchestrator state machine."""

    project_id: UUID
    phase: OrchestratorPhase = OrchestratorPhase.PLAN
    current_task_ids: list[UUID] = []
    completed_task_ids: list[UUID] = []
    failed_task_ids: list[UUID] = []
    pending_tasks: int = 0
    active_agents: list[UUID] = []
    escalation_reason: Optional[str] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)
