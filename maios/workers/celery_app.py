# maios/workers/celery_app.py
from celery import Celery

from maios.core.config import settings

app = Celery(
    "maios",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "maios.workers.tasks",
    ],
)

# Configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Beat schedule will be added later for heartbeat
app.conf.beat_schedule = {}
