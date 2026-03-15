from redis import Redis
from rq import Queue
from app.core.config import settings

redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Job 1: triage new incidents
incident_queue = Queue("incidents-queue", connection=redis_conn)

# Job 2: find + assign volunteer for an incident
assignment_queue = Queue("assignment-queue", connection=redis_conn)

# timeout checker
scheduler_queue = Queue("scheduler-queue", connection=redis_conn)