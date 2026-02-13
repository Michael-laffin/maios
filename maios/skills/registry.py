# maios/skills/registry.py
from typing import Any, Type

from maios.skills.base import BaseSkill


class SkillRegistry:
    """Registry for available skills."""

    def __init__(self):
        self._skills: dict[str, Type[BaseSkill]] = {}

    def register(self, skill_class: Type[BaseSkill]) -> None:
        """Register a skill class."""
        self._skills[skill_class.name] = skill_class

    def get(self, name: str) -> Type[BaseSkill] | None:
        """Get a skill class by name."""
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        """List all registered skill names."""
        return list(self._skills.keys())

    def get_skill(self, name: str, **kwargs) -> BaseSkill | None:
        """Instantiate a skill by name."""
        skill_class = self.get(name)
        if skill_class:
            return skill_class(**kwargs)
        return None


# Global registry
registry = SkillRegistry()


def register_skill(skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
    """Decorator to register a skill."""
    registry.register(skill_class)
    return skill_class
