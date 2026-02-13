"""Celery tasks for MAIOS."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from celery import shared_task
from sqlalchemy import select

from maios.core.agent_runtime import AgentRuntime
from maios.core.database import async_session
from maios.models.agent import Agent, AgentStatus
from maios.models.task import Task, TaskStatus
from maios.workers.celery_app import app

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_agent_task(self, task_id: str) -> dict:
    """Execute an agent task.

    This is a synchronous Celery task that wraps async execution.

    Args:
        task_id: UUID of the task to execute

    Returns:
        dict with status and result
    """
    return asyncio.run(_execute_agent_task_async(task_id, self))


async def _execute_agent_task_async(task_id: str, celery_task=None) -> dict:
    """Async implementation of task execution.

    Args:
        task_id: UUID string of the task to execute
        celery_task: The Celery task instance (for retry support)

    Returns:
        dict with execution status and result
    """
    task_uuid = UUID(task_id)

    async with async_session() as session:
        # 1. Get the task
        task_result = await session.execute(
            select(Task).where(Task.id == task_uuid)
        )
        task = task_result.scalar_one_or_none()

        if not task:
            logger.error(f"Task {task_id} not found")
            return {"status": "error", "error": "Task not found"}

        # 2. Check if task is still in an executable state
        if task.status not in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
            logger.info(f"Task {task_id} already {task.status}")
            return {
                "status": "skipped",
                "reason": f"Task already {task.status.value}",
            }

        # 3. Check if agent is assigned
        if not task.assigned_agent_id:
            logger.error(f"Task {task_id} has no assigned agent")
            return {"status": "error", "error": "No agent assigned"}

        # 4. Get the assigned agent
        agent_result = await session.execute(
            select(Agent).where(Agent.id == task.assigned_agent_id)
        )
        agent = agent_result.scalar_one_or_none()

        if not agent:
            logger.error(f"Agent {task.assigned_agent_id} not found")
            return {"status": "error", "error": "Agent not found"}

        # 5. Mark task as in progress, agent as working
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now(timezone.utc)
        agent.status = AgentStatus.WORKING
        await session.commit()

        try:
            # 6. Execute using AgentRuntime
            runtime = AgentRuntime(agent)

            # Build task prompt from title and description
            task_prompt = task.title
            if task.description:
                task_prompt = f"{task.title}\n\n{task.description}"

            result = await runtime.execute_task(
                task_id=task.id,
                task_title=task.title,
                task_description=task.description,
                context=task.task_metadata or {},
            )

            # 7. Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.progress_percent = 100

            # Extract result content
            if isinstance(result, dict):
                task.result = result.get("result") or result.get("content") or str(result)
            else:
                task.result = str(result)

            agent.status = AgentStatus.IDLE
            agent.tasks_completed += 1
            await session.commit()

            logger.info(f"Task {task_id} completed successfully")
            return {"status": "completed", "task_id": task_id}

        except Exception as e:
            # 8. Handle failure
            logger.exception(f"Task {task_id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            agent.status = AgentStatus.IDLE
            agent.tasks_failed += 1
            await session.commit()

            # Retry if under limit and celery_task is available
            if celery_task and task.retry_count < task.max_retries:
                logger.info(f"Retrying task {task_id} (attempt {task.retry_count}/{task.max_retries})")
                raise celery_task.retry(exc=e)

            return {"status": "failed", "error": str(e)}


# Keep the old task name for backwards compatibility
@app.task(bind=True)
def execute_task(self, task_id: str):
    """Execute a task (legacy endpoint, use execute_agent_task instead)."""
    return execute_agent_task(task_id)
