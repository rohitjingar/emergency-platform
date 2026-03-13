import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate
from app.models.incident import Incident
from app.core.exceptions import IncidentNotFoundError, DuplicateIncidentError
from app.core.config import settings
from app.db.redis_client import get_redis_client, is_redis_available

# ── Idempotency ──────────────────────────────────────────────────

def _build_idempotency_key(user_id: int, latitude: float, longitude: float) -> str:
    """
    Coordinates rounded to 3 decimal places (~111m precision).
    Keeps nearby reports from the same user within one key.
    """
    raw = f"{user_id}:{round(latitude, 3)}:{round(longitude, 3)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"idempotency:incident:{hashed}"

def _check_and_mark(key: str) -> bool:
    """
    Atomic check-and-set using Redis SET NX (set if not exists).
    Returns True if duplicate (key already existed).
    Returns False if new request (key was set successfully).

    Why SET NX instead of EXISTS + SETEX separately?
    EXISTS + SETEX = two round trips to Redis = race condition possible
    SET NX EX     = one round trip = atomic = no race condition
    """
    if not is_redis_available():
        # Redis down → fail open
        # A duplicate emergency report is safer than blocking a real one
        return False

    redis_client = get_redis_client()

    # SET key "1" EX 300 NX
    # NX = only set if key does NOT exist
    # EX = auto-expire after IDEMPOTENCY_WINDOW_SECONDS
    # Returns True if key was set (new request)
    # Returns None if key already existed (duplicate)
    result = redis_client.set(
        name=key,
        value="1",
        ex=settings.IDEMPOTENCY_WINDOW_SECONDS,
        nx=True
    )

    return result is None  # None = key existed = duplicate

# ── Redis Event Emission ─────────────────────────────────────────

def _emit_incident_event(incident: Incident) -> bool:
    """
    Push incident event to Redis queue for async processing.
    Returns True if emitted, False if Redis unavailable.
    Workers (Week 4) will consume from this queue.
    """
    if not is_redis_available():
        print(f"WARNING: Redis unavailable. Incident {incident.id} saved to DB but not queued.")
        return False

    event = {
        "event_type": "incident.created",
        "incident_id": incident.id,
        "type": incident.type,
        "priority": incident.priority,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "user_id": incident.user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    get_redis_client().lpush(
        settings.REDIS_INCIDENT_QUEUE,
        json.dumps(event)
    )
    return True

# ── Service Functions ────────────────────────────────────────────

def create_incident(db: Session, data: IncidentCreate, user_id: int) -> dict:
    # Step 1 — build key once, reuse for both check and mark
    idempotency_key = _build_idempotency_key(user_id, data.latitude, data.longitude)

    # Step 2 — atomic check + mark in one Redis round trip
    if _check_and_mark(idempotency_key):
        raise DuplicateIncidentError()

    # Step 3 — save to PostgreSQL
    incident = IncidentRepository(db).create(
        type=data.type,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        priority=data.priority or "medium",
        user_id=user_id
    )

    # Step 4 — emit event to Redis queue
    queued = _emit_incident_event(incident)

    return {"incident": incident, "queued": queued}

def get_incidents(db: Session, skip: int = 0, limit: int = 10) -> list[Incident]:
    return IncidentRepository(db).get_all(skip=skip, limit=limit)

def delete_incident(db: Session, incident_id: int) -> None:
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise IncidentNotFoundError(incident_id)
    repo.delete(incident)