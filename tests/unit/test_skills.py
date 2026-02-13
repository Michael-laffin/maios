# tests/unit/test_skills.py
import pytest


def test_skill_base_class():
    """Test skill base class structure."""
    from maios.skills.base import BaseSkill

    class TestSkill(BaseSkill):
        name = "test"
        description = "A test skill"

        async def execute(self, **kwargs):
            return {"result": "ok"}

    skill = TestSkill()
    assert skill.name == "test"
    assert skill.description == "A test skill"


def test_skill_registry():
    """Test skill registry."""
    from maios.skills.registry import SkillRegistry

    registry = SkillRegistry()
    assert registry is not None
