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


class TestReadFileSkill:
    """Tests for ReadFileSkill."""

    @pytest.mark.asyncio
    async def test_read_file_skill_exists(self):
        """Test ReadFileSkill is registered."""
        from maios.skills.builtin.read_file import ReadFileSkill

        skill = ReadFileSkill()
        assert skill.name == "read_file"
        assert "file:read" in skill.required_permissions

    @pytest.mark.asyncio
    async def test_read_file_validates_path(self):
        """Test ReadFileSkill validates file path."""
        from maios.skills.builtin.read_file import ReadFileSkill

        skill = ReadFileSkill()

        # Empty path
        result = await skill.execute(file_path="")
        assert result["status"] == "error"

        # Path traversal
        result = await skill.execute(file_path="../secret.txt")
        assert result["status"] == "error"

        # Absolute path
        result = await skill.execute(file_path="/etc/passwd")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_read_file_accepts_valid_input(self):
        """Test ReadFileSkill accepts valid input."""
        from maios.skills.builtin.read_file import ReadFileSkill

        skill = ReadFileSkill()
        result = await skill.execute(file_path="src/main.py", start_line=1, end_line=10)

        assert result["status"] == "pending"
        assert result["file_path"] == "src/main.py"


class TestWriteFileSkill:
    """Tests for WriteFileSkill."""

    @pytest.mark.asyncio
    async def test_write_file_skill_exists(self):
        """Test WriteFileSkill is registered."""
        from maios.skills.builtin.write_file import WriteFileSkill

        skill = WriteFileSkill()
        assert skill.name == "write_file"
        assert "file:write" in skill.required_permissions

    @pytest.mark.asyncio
    async def test_write_file_validates_path(self):
        """Test WriteFileSkill validates file path."""
        from maios.skills.builtin.write_file import WriteFileSkill

        skill = WriteFileSkill()

        # Empty path
        result = await skill.execute(file_path="", content="test")
        assert result["status"] == "error"

        # Path traversal
        result = await skill.execute(file_path="../secret.txt", content="test")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_write_file_validates_mode(self):
        """Test WriteFileSkill validates mode."""
        from maios.skills.builtin.write_file import WriteFileSkill

        skill = WriteFileSkill()
        result = await skill.execute(file_path="test.txt", content="test", mode="invalid")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_write_file_accepts_valid_input(self):
        """Test WriteFileSkill accepts valid input."""
        from maios.skills.builtin.write_file import WriteFileSkill

        skill = WriteFileSkill()
        result = await skill.execute(file_path="src/main.py", content="print('hello')", mode="write")

        assert result["status"] == "pending"
        assert result["content_length"] == len("print('hello')")


class TestSearchCodeSkill:
    """Tests for SearchCodeSkill."""

    @pytest.mark.asyncio
    async def test_search_code_skill_exists(self):
        """Test SearchCodeSkill is registered."""
        from maios.skills.builtin.search_code import SearchCodeSkill

        skill = SearchCodeSkill()
        assert skill.name == "search_code"
        assert "file:read" in skill.required_permissions

    @pytest.mark.asyncio
    async def test_search_code_validates_pattern(self):
        """Test SearchCodeSkill validates pattern."""
        from maios.skills.builtin.search_code import SearchCodeSkill

        skill = SearchCodeSkill()

        # Empty pattern
        result = await skill.execute(pattern="")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_search_code_validates_path(self):
        """Test SearchCodeSkill validates path."""
        from maios.skills.builtin.search_code import SearchCodeSkill

        skill = SearchCodeSkill()

        # Path traversal
        result = await skill.execute(pattern="test", path="../secret")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_search_code_accepts_valid_input(self):
        """Test SearchCodeSkill accepts valid input."""
        from maios.skills.builtin.search_code import SearchCodeSkill

        skill = SearchCodeSkill()
        result = await skill.execute(
            pattern="def test_",
            path="tests/",
            file_pattern="*.py",
            is_regex=True,
        )

        assert result["status"] == "pending"
        assert result["pattern"] == "def test_"


class TestRunTestsSkill:
    """Tests for RunTestsSkill."""

    @pytest.mark.asyncio
    async def test_run_tests_skill_exists(self):
        """Test RunTestsSkill is registered."""
        from maios.skills.builtin.run_tests import RunTestsSkill

        skill = RunTestsSkill()
        assert skill.name == "run_tests"
        assert "exec" in skill.required_permissions

    @pytest.mark.asyncio
    async def test_run_tests_validates_framework(self):
        """Test RunTestsSkill validates framework."""
        from maios.skills.builtin.run_tests import RunTestsSkill

        skill = RunTestsSkill()
        result = await skill.execute(framework="invalid")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_run_tests_validates_path(self):
        """Test RunTestsSkill validates path."""
        from maios.skills.builtin.run_tests import RunTestsSkill

        skill = RunTestsSkill()

        # Path traversal
        result = await skill.execute(test_path="../secret")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_run_tests_accepts_valid_input(self):
        """Test RunTestsSkill accepts valid input."""
        from maios.skills.builtin.run_tests import RunTestsSkill

        skill = RunTestsSkill()
        result = await skill.execute(
            test_path="tests/unit/",
            framework="pytest",
            coverage=True,
            verbose=True,
        )

        assert result["status"] == "pending"
        assert result["framework"] == "pytest"


class TestGitOperationSkill:
    """Tests for GitOperationSkill."""

    @pytest.mark.asyncio
    async def test_git_operation_skill_exists(self):
        """Test GitOperationSkill is registered."""
        from maios.skills.builtin.git_operation import GitOperationSkill

        skill = GitOperationSkill()
        assert skill.name == "git_operation"

    @pytest.mark.asyncio
    async def test_git_operation_validates_operation(self):
        """Test GitOperationSkill validates operation."""
        from maios.skills.builtin.git_operation import GitOperationSkill

        skill = GitOperationSkill()
        result = await skill.execute(operation="invalid")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_git_commit_requires_message(self):
        """Test GitOperationSkill requires message for commit."""
        from maios.skills.builtin.git_operation import GitOperationSkill

        skill = GitOperationSkill()
        result = await skill.execute(operation="commit")

        assert result["status"] == "error"
        assert "message" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_git_branch_requires_name(self):
        """Test GitOperationSkill requires name for branch operations."""
        from maios.skills.builtin.git_operation import GitOperationSkill

        skill = GitOperationSkill()
        result = await skill.execute(operation="branch")

        assert result["status"] == "error"
        assert "branch" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_git_operation_accepts_valid_input(self):
        """Test GitOperationSkill accepts valid input."""
        from maios.skills.builtin.git_operation import GitOperationSkill

        skill = GitOperationSkill()

        # Status operation (read-only)
        result = await skill.execute(operation="status")
        assert result["status"] == "pending"

        # Commit with message
        result = await skill.execute(operation="commit", message="Add feature")
        assert result["status"] == "pending"

        # Branch with name
        result = await skill.execute(operation="branch", branch="feature-xyz")
        assert result["status"] == "pending"


class TestSkillRegistration:
    """Tests for skill registration."""

    def test_all_skills_registered(self):
        """Test that all skills are registered in the global registry."""
        from maios.skills.registry import registry

        expected_skills = [
            "execute_code",
            "read_file",
            "write_file",
            "search_code",
            "run_tests",
            "git_operation",
        ]

        for skill_name in expected_skills:
            assert skill_name in registry.list_skills(), f"Skill {skill_name} not registered"

    def test_get_skill_by_name(self):
        """Test retrieving skill by name."""
        from maios.skills.registry import registry

        skill_class = registry.get("read_file")
        assert skill_class is not None
        assert skill_class.name == "read_file"

    def test_instantiate_skill(self):
        """Test instantiating a skill from registry."""
        from maios.skills.registry import registry

        skill = registry.get_skill("read_file")
        assert skill is not None
        assert skill.name == "read_file"

