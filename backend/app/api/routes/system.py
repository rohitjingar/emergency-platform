# app/api/routes/system.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.redis_client import is_redis_available, get_redis_client
from app.core.circuit_breaker import get_circuit_status

router = APIRouter(prefix="/system", tags=["System"])

# ── Health Check ─────────────────────────────────────

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Full system health check.
    Used by load balancer + DevOps monitoring.
    Checks: API, PostgreSQL, Redis, Circuit Breaker.
    """
    health = {
        "api": "ok",
        "postgres": "ok",
        "redis": "ok",
        "circuit_breaker": "ok",
        "overall": "ok"
    }
    issues = []

    # check PostgreSQL
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        health["postgres"] = "down"
        issues.append(f"postgres: {str(e)[:50]}")

    # check Redis
    if not is_redis_available():
        health["redis"] = "down"
        issues.append("redis: connection failed")
    else:
        try:
            get_redis_client().ping()
        except Exception as e:
            health["redis"] = "down"
            issues.append(f"redis: {str(e)[:50]}")

    # check circuit breaker
    cb_status = get_circuit_status()
    if cb_status["state"] == "open":
        health["circuit_breaker"] = "open"
        issues.append(
            f"circuit_breaker: OPEN "
            f"({cb_status['failures']}/{cb_status['threshold']} failures)"
        )
    elif cb_status["state"] == "half_open":
        health["circuit_breaker"] = "half_open"
        issues.append("circuit_breaker: HALF_OPEN — testing recovery")

    # overall status
    if any(v in ("down",) for v in health.values()):
        health["overall"] = "degraded"
    elif cb_status["state"] == "open":
        health["overall"] = "degraded"

    health["issues"] = issues
    health["circuit_breaker_detail"] = cb_status

    return health

# ── Circuit Breaker ───────────────────────────────────

@router.get("/circuit-breaker")
def get_circuit_breaker():
    """
    Current circuit breaker state.
    CLOSED  = LLM API healthy, all calls going through
    OPEN    = LLM API failing, fallback rule-based classifier active
    HALF_OPEN = testing recovery, one call allowed through
    """
    return get_circuit_status()

@router.post("/circuit-breaker/simulate-failure")
def simulate_failure():
    """
    Manually record a failure.
    For testing circuit breaker behavior only.
    In production — remove or restrict to internal network.
    """
    from app.core.circuit_breaker import record_failure
    record_failure()
    return get_circuit_status()

@router.post("/circuit-breaker/reset")
def reset_circuit():
    """
    Manually reset circuit to CLOSED.
    Used by DevOps when LLM API is confirmed healthy again.
    """
    from app.core.circuit_breaker import record_success
    record_success()
    return get_circuit_status()

# ── Queue Stats ───────────────────────────────────────

@router.get("/queues")
def get_queue_stats():
    """
    RQ queue depths — how many jobs are waiting.
    Useful for detecting backlogs during disaster surge.
    """
    if not is_redis_available():
        return {"error": "Redis unavailable"}

    try:
        from rq import Queue
        from app.workers.queues import redis_conn

        incident_q = Queue("incidents-queue", connection=redis_conn)
        assignment_q = Queue("assignment-queue", connection=redis_conn)
        scheduler_q = Queue("scheduler-queue", connection=redis_conn)

        return {
            "incidents_queue": {
                "waiting": len(incident_q),
                "failed": incident_q.failed_job_registry.count
            },
            "assignment_queue": {
                "waiting": len(assignment_q),
                "failed": assignment_q.failed_job_registry.count
            },
            "scheduler_queue": {
                "waiting": len(scheduler_q),
                "failed": scheduler_q.failed_job_registry.count
            }
        }
    except Exception as e:
        return {"error": str(e)}