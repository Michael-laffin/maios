# maios/skills/base.py
from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC):
    """Base class for all skills."""

    name: str
    description: str
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    required_permissions: list[str] = []

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the skill."""
        pass

    def validate_permissions(self, agent_permissions: list[str]) -> bool:
        """Check if agent has required permissions."""
        return all(p in agent_permissions for p in self.required_permissions)
