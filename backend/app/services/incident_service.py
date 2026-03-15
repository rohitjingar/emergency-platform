import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.repositories.incident_repository import IncidentRepository
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate
from app.core.exceptions import IncidentNotFoundError, DuplicateIncidentError
from app.core.config import settings
from app.db.redis_client import get_redis_client, is_redis_available

def _build_idempotency_key(user_id: int, latitude: float, longitude: float) -> str:
    raw = f"{user_id}:{round(latitude, 3)}:{round(longitude, 3)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"idempotency:incident:{hashed}"

def _check_and_mark(key: str) -> bool:
    if not is_redis_available():
        return False
    result = get_redis_client().set(
        name=key,
        value="1",
        ex=settings.IDEMPOTENCY_WINDOW_SECONDS,
        nx=True
    )
    return result is None

def _enqueue_incident(incident_id: int) -> bool:
    
    if not is_redis_available():
        return False
    try:
        from app.workers.queues import incident_queue
        from app.workers.incident_worker import process_incident
        job = incident_queue.enqueue(
            process_incident,
            incident_id,
            job_timeout=300
        )
        
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

def create_incident(db: Session, data: IncidentCreate, user_id: int) -> dict:
    # Step 1 — idempotency check
    idempotency_key = _build_idempotency_key(user_id, data.latitude, data.longitude)
    if _check_and_mark(idempotency_key):
        raise DuplicateIncidentError()

    # Step 2 — save to DB with status "open"
    incident = IncidentRepository(db).create(
        type=data.type,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        priority=data.priority or "medium",
        user_id=user_id
    )

    # Step 3 — enqueue background job
    # triage + matching happens in worker, not here
    queued = _enqueue_incident(incident.id)

    if not queued:
        # Redis down — run synchronously as fallback
        from app.agents.triage_agent import run_triage
        try:
            triage = run_triage(incident.description, incident.type)
            incident.severity = triage["severity"]
            incident.confidence = triage["confidence"]
            incident.reasoning = triage["reasoning"]
            incident.rag_used = "yes" if triage["rag_used"] else "no"
            db.commit()
            db.refresh(incident)
        except Exception as e:
            print(f"WARNING: Sync triage also failed: {e}")

    return {
        "incident": incident,
        "queued": queued
    }

def get_incidents(db: Session, skip: int = 0, limit: int = 10) -> list[Incident]:
    return IncidentRepository(db).get_all(skip=skip, limit=limit)

def delete_incident(db: Session, incident_id: int) -> None:
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise IncidentNotFoundError(incident_id)
    repo.delete(incident)