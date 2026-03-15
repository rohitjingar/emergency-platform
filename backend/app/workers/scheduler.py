# app/workers/scheduler.py
from datetime import datetime
from rq_scheduler import Scheduler
from app.workers.queues import redis_conn
from app.workers.timeout_worker import check_timed_out_assignments


def start_scheduler() -> None:
    scheduler = Scheduler(
        queue_name="scheduler-queue",
        connection=redis_conn
    )

    # cancel existing jobs
    existing_jobs = list(scheduler.get_jobs())
    if existing_jobs:
        for job in existing_jobs:
            scheduler.cancel(job)
        print(f"Cancelled {len(existing_jobs)} existing scheduled jobs")

    # register timeout checker every 10 seconds
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=check_timed_out_assignments,
        interval=10,
        repeat=None
    )

    print("Registered: check_timed_out_assignments → every 10 seconds")
    print("Now start: rq worker scheduler-queue")


if __name__ == "__main__":
    start_scheduler()