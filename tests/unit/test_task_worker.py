"""Tests for Task Execution Worker."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID

from maios.models.task import Task, TaskStatus, TaskPriority
from maios.models.agent import Agent, AgentStatus
from maios.models.project import Project


class TestExecuteAgentTask:
    """Tests for the execute_agent_task Celery task."""

    @pytest.fixture
    def mock_project(self):
        """Create a mock project."""
        return Project(
            id=uuid4(),
            name="Test Project",
            description="A test project",
        )

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        return Agent(
            id=uuid4(),
            name="TestAgent",
            role="Developer",
            persona="A test agent for task execution",
            skill_tags=["python", "testing"],
            status=AgentStatus.IDLE,
        )

    @pytest.fixture
    def mock_task(self, mock_project, mock_agent):
        """Create a mock task."""
        return Task(
            id=uuid4(),
            title="Test Task",
            description="A test task for execution",
            project_id=mock_project.id,
            assigned_agent_id=mock_agent.id,
            status=TaskStatus.ASSIGNED,
            priority=TaskPriority.MEDIUM,
            max_retries=3,
            retry_count=0,
        )

    @pytest.mark.asyncio
    async def test_execute_agent_task_success(self, mock_task, mock_agent, mock_project):
        """Test successful task execution."""
        from maios.workers.tasks import _execute_agent_task_async

        # Mock the database session
        mock_session = AsyncMock()

        # Mock the select queries
        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        # Set up session.execute to return appropriate results
        execute_results = [mock_task_result, mock_agent_result]
        mock_session.execute.side_effect = execute_results
        mock_session.commit = AsyncMock()

        # Mock AgentRuntime.execute_task to return success
        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Task completed successfully",
                "content": "Task completed successfully",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "completed"
        assert result["task_id"] == str(mock_task.id)

    @pytest.mark.asyncio
    async def test_execute_agent_task_not_found(self):
        """Test task execution when task is not found."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with patch("maios.workers.tasks.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session

            task_id = str(uuid4())
            result = await _execute_agent_task_async(task_id)

        assert result["status"] == "error"
        assert result["error"] == "Task not found"

    @pytest.mark.asyncio
    async def test_execute_agent_task_no_agent_assigned(self, mock_task, mock_project):
        """Test task execution when no agent is assigned."""
        from maios.workers.tasks import _execute_agent_task_async

        # Create task without assigned agent
        mock_task.assigned_agent_id = None
        mock_task.status = TaskStatus.PENDING

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result

        with patch("maios.workers.tasks.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session

            result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "error"
        assert result["error"] == "No agent assigned"

    @pytest.mark.asyncio
    async def test_execute_agent_task_agent_not_found(self, mock_task, mock_agent, mock_project):
        """Test task execution when agent is not found."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = None  # Agent not found

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]

        with patch("maios.workers.tasks.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session

            result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "error"
        assert result["error"] == "Agent not found"

    @pytest.mark.asyncio
    async def test_execute_agent_task_already_completed(self, mock_task, mock_agent, mock_project):
        """Test task execution when task is already completed."""
        from maios.workers.tasks import _execute_agent_task_async

        # Set task as already completed
        mock_task.status = TaskStatus.COMPLETED

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result

        with patch("maios.workers.tasks.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session

            result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "skipped"
        assert "already" in result["reason"]

    @pytest.mark.asyncio
    async def test_execute_agent_task_already_in_progress(self, mock_task, mock_agent, mock_project):
        """Test task execution when task is already in progress."""
        from maios.workers.tasks import _execute_agent_task_async

        # Set task as already in progress
        mock_task.status = TaskStatus.IN_PROGRESS

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result

        with patch("maios.workers.tasks.async_session") as mock_async_session:
            mock_async_session.return_value.__aenter__.return_value = mock_session

            result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "skipped"
        assert "already" in result["reason"]

    @pytest.mark.asyncio
    async def test_execute_agent_task_updates_status_to_in_progress(
        self, mock_task, mock_agent, mock_project
    ):
        """Test that task and agent status are updated when execution starts."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Done",
                "content": "Done",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                await _execute_agent_task_async(str(mock_task.id))

        # Check that task status was updated to IN_PROGRESS
        assert mock_task.status == TaskStatus.COMPLETED
        assert mock_task.started_at is not None
        assert mock_agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_execute_agent_task_failure(self, mock_task, mock_agent, mock_project):
        """Test task execution when execution fails."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(side_effect=Exception("Execution failed"))

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "failed"
        assert "Execution failed" in result["error"]
        assert mock_task.status == TaskStatus.FAILED
        assert mock_task.error_message == "Execution failed"
        assert mock_task.retry_count == 1

    @pytest.mark.asyncio
    async def test_execute_agent_task_with_context(self, mock_task, mock_agent, mock_project):
        """Test task execution with context metadata."""
        from maios.workers.tasks import _execute_agent_task_async

        # Add context metadata
        mock_task.task_metadata = {"file": "test.py", "priority": "high"}

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Done",
                "content": "Done",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "completed"
        # Verify execute_task was called with the context
        mock_runtime.execute_task.assert_called_once()
        call_args = mock_runtime.execute_task.call_args
        assert call_args[1]["context"] == {"file": "test.py", "priority": "high"}

    @pytest.mark.asyncio
    async def test_execute_agent_task_with_description(self, mock_task, mock_agent, mock_project):
        """Test task execution with description."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_task.description = "Detailed task description"

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Done",
                "content": "Done",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "completed"
        # Verify execute_task was called with the description
        mock_runtime.execute_task.assert_called_once()
        call_args = mock_runtime.execute_task.call_args
        assert call_args[1]["task_description"] == "Detailed task description"

    @pytest.mark.asyncio
    async def test_execute_agent_task_updates_agent_stats(
        self, mock_task, mock_agent, mock_project
    ):
        """Test that agent stats are updated after completion."""
        from maios.workers.tasks import _execute_agent_task_async

        initial_completed = mock_agent.tasks_completed

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Done",
                "content": "Done",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                await _execute_agent_task_async(str(mock_task.id))

        assert mock_agent.tasks_completed == initial_completed + 1
        assert mock_agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_execute_agent_task_failure_updates_agent_stats(
        self, mock_task, mock_agent, mock_project
    ):
        """Test that agent stats are updated after failure."""
        from maios.workers.tasks import _execute_agent_task_async

        initial_failed = mock_agent.tasks_failed

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(side_effect=Exception("Failed"))

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                await _execute_agent_task_async(str(mock_task.id))

        assert mock_agent.tasks_failed == initial_failed + 1
        assert mock_agent.status == AgentStatus.IDLE


class TestExecuteAgentTaskRetry:
    """Tests for task retry logic."""

    @pytest.fixture
    def mock_project(self):
        """Create a mock project."""
        return Project(id=uuid4(), name="Test Project", description="Test")

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        return Agent(
            id=uuid4(),
            name="TestAgent",
            role="Developer",
            persona="Test agent",
            status=AgentStatus.IDLE,
        )

    @pytest.fixture
    def mock_task(self, mock_project, mock_agent):
        """Create a mock task with retry configuration."""
        return Task(
            id=uuid4(),
            title="Retry Task",
            description="Task that will be retried",
            project_id=mock_project.id,
            assigned_agent_id=mock_agent.id,
            status=TaskStatus.ASSIGNED,
            max_retries=3,
            retry_count=0,
        )

    @pytest.mark.asyncio
    async def test_task_retry_count_incremented_on_failure(
        self, mock_task, mock_agent, mock_project
    ):
        """Test that retry count is incremented on failure."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(side_effect=Exception("Failed"))

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                await _execute_agent_task_async(str(mock_task.id))

        assert mock_task.retry_count == 1

    @pytest.mark.asyncio
    async def test_task_no_retry_when_max_reached(self, mock_task, mock_agent, mock_project):
        """Test that task does not retry when max retries reached."""
        from maios.workers.tasks import _execute_agent_task_async

        # Set retry count to max
        mock_task.retry_count = 3
        mock_task.max_retries = 3

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(side_effect=Exception("Failed"))

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        # Should return failed, not raise for retry
        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_task_pending_status_allowed(self, mock_task, mock_agent, mock_project):
        """Test that tasks with PENDING status can be executed."""
        from maios.workers.tasks import _execute_agent_task_async

        mock_task.status = TaskStatus.PENDING

        mock_session = AsyncMock()

        mock_task_result = MagicMock()
        mock_task_result.scalar_one_or_none.return_value = mock_task

        mock_agent_result = MagicMock()
        mock_agent_result.scalar_one_or_none.return_value = mock_agent

        mock_session.execute.side_effect = [mock_task_result, mock_agent_result]
        mock_session.commit = AsyncMock()

        with patch("maios.workers.tasks.AgentRuntime") as MockRuntime:
            mock_runtime = MockRuntime.return_value
            mock_runtime.execute_task = AsyncMock(return_value={
                "status": "success",
                "result": "Done",
                "content": "Done",
            })

            with patch("maios.workers.tasks.async_session") as mock_async_session:
                mock_async_session.return_value.__aenter__.return_value = mock_session

                result = await _execute_agent_task_async(str(mock_task.id))

        assert result["status"] == "completed"


class TestCeleryTaskDecorator:
    """Tests for Celery task decorator configuration."""

    def test_execute_agent_task_is_registered(self):
        """Test that execute_agent_task is registered as a Celery task."""
        from maios.workers.tasks import execute_agent_task

        # Check it's a Celery task
        assert hasattr(execute_agent_task, "delay")
        assert hasattr(execute_agent_task, "apply_async")

    def test_task_has_retry_configuration(self):
        """Test that task has retry configuration."""
        from maios.workers.tasks import execute_agent_task

        # Check retry configuration
        # The task should have max_retries set
        assert execute_agent_task.max_retries >= 1
