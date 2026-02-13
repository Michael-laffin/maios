# tests/unit/test_models.py
"""Tests for core data models."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest


class TestAgentModel:
    """Tests for the Agent model."""

    def test_agent_model_creation(self):
        """Test that an Agent can be created with required fields."""
        from maios.models.agent import Agent, AgentStatus

        agent = Agent(
            name="TestAgent",
            role="Developer",
            persona="A helpful coding assistant",
        )

        assert agent.name == "TestAgent"
        assert agent.role == "Developer"
        assert agent.persona == "A helpful coding assistant"
        assert agent.status == AgentStatus.IDLE
        assert agent.model_provider == "z.ai"
        assert agent.model_name == "glm-4-plus"
        assert agent.performance_score == 0.0
        assert agent.tasks_completed == 0
        assert agent.tasks_failed == 0
        assert agent.is_active is True
        assert isinstance(agent.id, UUID)

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        from maios.models.agent import AgentStatus

        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.WORKING.value == "working"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.DISABLED.value == "disabled"

    def test_agent_update_timestamp(self):
        """Test that update_timestamp updates the timestamp."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test")
        old_updated = agent.updated_at

        agent.update_timestamp()

        assert agent.updated_at > old_updated

    def test_agent_mark_working(self):
        """Test marking an agent as working."""
        from maios.models.agent import Agent, AgentStatus

        agent = Agent(name="Test", role="Test")
        task_id = uuid4()

        agent.mark_working(task_id)

        assert agent.status == AgentStatus.WORKING
        assert agent.current_task_id == task_id

    def test_agent_mark_idle(self):
        """Test marking an agent as idle."""
        from maios.models.agent import Agent, AgentStatus

        agent = Agent(name="Test", role="Test", status=AgentStatus.WORKING, current_task_id=uuid4())

        agent.mark_idle()

        assert agent.status == AgentStatus.IDLE
        assert agent.current_task_id is None

    def test_agent_record_task_completion(self):
        """Test recording task completion."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test")

        agent.record_task_completion(success=True)

        assert agent.tasks_completed == 1
        assert agent.tasks_failed == 0
        assert agent.performance_score == 1.0

        agent.record_task_completion(success=False)

        assert agent.tasks_completed == 1
        assert agent.tasks_failed == 1
        assert agent.performance_score == 0.5

    def test_agent_permission_check(self):
        """Test permission checking."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test", permissions=["read", "write"])

        assert agent.has_permission("read") is True
        assert agent.has_permission("write") is True
        assert agent.has_permission("execute") is False

    def test_agent_wildcard_permission(self):
        """Test wildcard permission."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test", permissions=["*"])

        assert agent.has_permission("anything") is True

    def test_agent_skill_check(self):
        """Test skill checking."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test", skill_tags=["python", "fastapi"])

        assert agent.has_skill("python") is True
        assert agent.has_skill("javascript") is False

    def test_agent_communication_access(self):
        """Test communication access."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test", communication_access=["agent-1", "agent-2"])

        assert agent.can_communicate_with("agent-1") is True
        assert agent.can_communicate_with("agent-3") is False

    def test_agent_wildcard_communication(self):
        """Test wildcard communication access."""
        from maios.models.agent import Agent

        agent = Agent(name="Test", role="Test", communication_access=["*"])

        assert agent.can_communicate_with("any-agent") is True


class TestTaskModel:
    """Tests for the Task model."""

    def test_task_model_creation(self):
        """Test that a Task can be created with required fields."""
        from maios.models.task import Task, TaskPriority, TaskStatus

        project_id = uuid4()
        task = Task(title="Test Task", project_id=project_id)

        assert task.title == "Test Task"
        assert task.project_id == project_id
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.progress_percent == 0
        assert task.timeout_minutes == 30
        assert task.max_retries == 3
        assert task.retry_count == 0
        assert task.complexity == "medium"
        assert isinstance(task.id, UUID)

    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        from maios.models.task import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.ASSIGNED.value == "assigned"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_task_priority_enum(self):
        """Test TaskPriority enum values."""
        from maios.models.task import TaskPriority

        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"

    def test_task_start(self):
        """Test starting a task."""
        from maios.models.task import Task, TaskStatus

        task = Task(title="Test", project_id=uuid4())

        task.start()

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None

    def test_task_complete(self):
        """Test completing a task."""
        from maios.models.task import Task, TaskStatus

        task = Task(title="Test", project_id=uuid4(), status=TaskStatus.IN_PROGRESS)

        task.complete(result="Done!")

        assert task.status == TaskStatus.COMPLETED
        assert task.result == "Done!"
        assert task.progress_percent == 100
        assert task.completed_at is not None

    def test_task_fail(self):
        """Test failing a task."""
        from maios.models.task import Task, TaskStatus

        task = Task(title="Test", project_id=uuid4(), status=TaskStatus.IN_PROGRESS)

        task.fail(error_message="Something went wrong")

        assert task.status == TaskStatus.FAILED
        assert task.error_message == "Something went wrong"

    def test_task_cancel(self):
        """Test canceling a task."""
        from maios.models.task import Task, TaskStatus

        task = Task(title="Test", project_id=uuid4())

        task.cancel()

        assert task.status == TaskStatus.CANCELLED

    def test_task_assign(self):
        """Test assigning a task."""
        from maios.models.task import Task, TaskStatus

        task = Task(title="Test", project_id=uuid4())
        agent_id = uuid4()

        task.assign(agent_id)

        assert task.status == TaskStatus.ASSIGNED
        assert task.assigned_agent_id == agent_id

    def test_task_retry(self):
        """Test task retry logic."""
        from maios.models.task import Task

        task = Task(title="Test", project_id=uuid4(), max_retries=3)

        assert task.can_retry() is True

        task.increment_retry()
        assert task.retry_count == 1
        assert task.can_retry() is True

        task.retry_count = 3
        assert task.can_retry() is False

    def test_task_progress(self):
        """Test setting task progress."""
        from maios.models.task import Task

        task = Task(title="Test", project_id=uuid4())

        task.set_progress(50)

        assert task.progress_percent == 50

        # Test bounds
        task.set_progress(150)
        assert task.progress_percent == 100

        task.set_progress(-10)
        assert task.progress_percent == 0

    def test_task_dependencies(self):
        """Test task dependencies."""
        from maios.models.task import Task

        task = Task(title="Test", project_id=uuid4())
        dep_id = uuid4()

        task.add_dependency(dep_id)

        assert dep_id in task.dependencies

        task.remove_dependency(dep_id)

        assert dep_id not in task.dependencies

    def test_task_is_subtask(self):
        """Test checking if task is a subtask."""
        from maios.models.task import Task

        task = Task(title="Test", project_id=uuid4())
        assert task.is_subtask() is False

        task.parent_task_id = uuid4()
        assert task.is_subtask() is True

    def test_task_metadata(self):
        """Test task metadata."""
        from maios.models.task import Task

        task = Task(title="Test", project_id=uuid4())

        assert task.task_metadata == {}

        task.task_metadata["key"] = "value"
        assert task.task_metadata["key"] == "value"


class TestProjectModel:
    """Tests for the Project model."""

    def test_project_model_creation(self):
        """Test that a Project can be created with required fields."""
        from maios.models.project import Project, ProjectStatus

        project = Project(name="Test Project")

        assert project.name == "Test Project"
        assert project.status == ProjectStatus.PLANNING
        assert project.orchestrator_phase == "PLAN"
        assert project.tech_stack == []
        assert project.constraints == {}
        assert project.context_files == []
        assert project.project_metadata == {}
        assert isinstance(project.id, UUID)

    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        from maios.models.project import ProjectStatus

        assert ProjectStatus.PLANNING.value == "planning"
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.PAUSED.value == "paused"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.CANCELLED.value == "cancelled"

    def test_project_activate(self):
        """Test activating a project."""
        from maios.models.project import Project, ProjectStatus

        project = Project(name="Test")

        project.activate()

        assert project.status == ProjectStatus.ACTIVE

    def test_project_pause(self):
        """Test pausing a project."""
        from maios.models.project import Project, ProjectStatus

        project = Project(name="Test", status=ProjectStatus.ACTIVE)

        project.pause()

        assert project.status == ProjectStatus.PAUSED

    def test_project_complete(self):
        """Test completing a project."""
        from maios.models.project import Project, ProjectStatus

        project = Project(name="Test", status=ProjectStatus.ACTIVE)

        project.complete()

        assert project.status == ProjectStatus.COMPLETED

    def test_project_tech_stack(self):
        """Test tech stack management."""
        from maios.models.project import Project

        project = Project(name="Test")

        project.add_tech("Python")
        assert "Python" in project.tech_stack

        project.add_tech("Python")  # Should not duplicate
        assert len(project.tech_stack) == 1

        project.remove_tech("Python")
        assert "Python" not in project.tech_stack

    def test_project_context_files(self):
        """Test context file management."""
        from maios.models.project import Project

        project = Project(name="Test")

        project.add_context_file("/path/to/file.py")
        assert "/path/to/file.py" in project.context_files

        project.remove_context_file("/path/to/file.py")
        assert "/path/to/file.py" not in project.context_files

    def test_project_constraints(self):
        """Test constraint management."""
        from maios.models.project import Project

        project = Project(name="Test")

        project.set_constraint("max_lines", 500)
        assert project.get_constraint("max_lines") == 500
        assert project.get_constraint("nonexistent", "default") == "default"

        project.remove_constraint("max_lines")
        assert "max_lines" not in project.constraints

    def test_project_metadata(self):
        """Test metadata management."""
        from maios.models.project import Project

        project = Project(name="Test")

        project.set_metadata("key", "value")
        assert project.get_metadata("key") == "value"

    def test_project_is_editable(self):
        """Test is_editable check."""
        from maios.models.project import Project, ProjectStatus

        project = Project(name="Test")
        assert project.is_editable() is True

        project.status = ProjectStatus.ACTIVE
        assert project.is_editable() is True

        project.status = ProjectStatus.COMPLETED
        assert project.is_editable() is False


class TestMemoryModel:
    """Tests for the MemoryEntry model."""

    def test_memory_entry_creation(self):
        """Test that a MemoryEntry can be created with required fields."""
        from maios.models.memory import MemoryEntry, MemoryType

        memory = MemoryEntry(content="This is a test memory")

        assert memory.content == "This is a test memory"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.importance == 0.5
        assert memory.access_count == 0
        assert memory.keywords == []
        assert memory.tags == []
        assert isinstance(memory.id, UUID)

    def test_memory_type_enum(self):
        """Test MemoryType enum values."""
        from maios.models.memory import MemoryType

        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.PROCEDURAL.value == "procedural"
        assert MemoryType.WORKING.value == "working"

    def test_memory_access(self):
        """Test memory access tracking."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test")

        memory.access()

        assert memory.access_count == 1
        assert memory.last_accessed is not None

    def test_memory_keywords(self):
        """Test keyword management."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test")

        memory.add_keyword("python")
        assert memory.has_keyword("python") is True
        assert memory.has_keyword("javascript") is False

        # Test case insensitivity
        assert memory.has_keyword("PYTHON") is True

        memory.remove_keyword("python")
        assert memory.has_keyword("python") is False

    def test_memory_tags(self):
        """Test tag management."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test")

        memory.add_tag("important")
        assert memory.has_tag("important") is True

        memory.remove_tag("important")
        assert memory.has_tag("important") is False

    def test_memory_importance(self):
        """Test importance setting."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test")

        memory.set_importance(0.8)
        assert memory.importance == 0.8

        # Test bounds
        memory.set_importance(1.5)
        assert memory.importance == 1.0

        memory.set_importance(-0.5)
        assert memory.importance == 0.0

    def test_memory_embedding(self):
        """Test embedding management."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test")

        assert memory.has_embedding() is False

        memory.set_embedding([0.1, 0.2, 0.3])

        assert memory.has_embedding() is True
        assert memory.embedding == [0.1, 0.2, 0.3]

    def test_memory_type_checks(self):
        """Test memory type check methods."""
        from maios.models.memory import MemoryEntry, MemoryType

        memory = MemoryEntry(content="Test", memory_type=MemoryType.EPISODIC)
        assert memory.is_episodic() is True
        assert memory.is_semantic() is False

        memory.memory_type = MemoryType.SEMANTIC
        assert memory.is_semantic() is True

        memory.memory_type = MemoryType.PROCEDURAL
        assert memory.is_procedural() is True

        memory.memory_type = MemoryType.WORKING
        assert memory.is_working() is True

    def test_memory_relevance_score(self):
        """Test relevance score calculation."""
        from maios.models.memory import MemoryEntry

        memory = MemoryEntry(content="Test", importance=0.5)

        # Low access count
        score = memory.get_relevance_score()
        assert 0 <= score <= 1

        # High access count increases score
        for _ in range(100):
            memory.access()

        new_score = memory.get_relevance_score()
        assert new_score > score

    def test_memory_is_related_to(self):
        """Test related entity checking."""
        from maios.models.memory import MemoryEntry

        agent_id = uuid4()
        project_id = uuid4()
        task_id = uuid4()

        memory = MemoryEntry(
            content="Test",
            agent_id=agent_id,
            project_id=project_id,
        )

        assert memory.is_related_to(agent_id=agent_id) is True
        assert memory.is_related_to(project_id=project_id) is True
        assert memory.is_related_to(task_id=task_id) is False
        assert memory.is_related_to(task_id=task_id) is False


class TestModelImports:
    """Test that all models can be imported from the models package."""

    def test_import_from_package(self):
        """Test importing all models from the package."""
        from maios.models import (
            Agent,
            AgentStatus,
            MemoryEntry,
            MemoryType,
            Project,
            ProjectStatus,
            Task,
            TaskPriority,
            TaskStatus,
        )

        # Verify they are the correct types
        assert Agent is not None
        assert AgentStatus is not None
        assert Task is not None
        assert TaskStatus is not None
        assert TaskPriority is not None
        assert Project is not None
        assert ProjectStatus is not None
        assert MemoryEntry is not None
        assert MemoryType is not None
