# maios/workers/tasks.py
from maios.workers.celery_app import app


@app.task(bind=True)
def execute_task(self, task_id: str):
    """Execute a task (placeholder for now)."""
    # Will be implemented in future phases
    return {"task_id": task_id, "status": "pending"}
