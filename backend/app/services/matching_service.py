# app/services/matching_service.py
from sqlalchemy.orm import Session
from app.db.redis_client import get_redis_client, is_redis_available

INCIDENT_SKILL_MAP = {
    "flood":    "flood",
    "fire":     "fire",
    "medical":  "medical",
    "accident": "rescue",
    "other":    "rescue",
}

MAX_ASSIGNMENT_ATTEMPTS = 5

def _get_required_skill(incident_type: str) -> str:
    return INCIDENT_SKILL_MAP.get(incident_type, "rescue")

# ── Redis keys ───────────────────────────────────────────────────

def _unavailable_key(volunteer_id: int, incident_id: int) -> str:
    return f"volunteer:unavailable:{volunteer_id}:{incident_id}"

def _timedout_key(volunteer_id: int, incident_id: int) -> str:
    return f"volunteer:timedout:{volunteer_id}:{incident_id}"

def _lock_key(volunteer_id: int) -> str:
    return f"volunteer:lock:{volunteer_id}"

def _cache_key(volunteer_id: int) -> str:
    return f"volunteer:available:{volunteer_id}"

# ── Cache-Aside availability ─────────────────────────────────────

def set_volunteer_cache(volunteer_id: int, status: str) -> None:
    if not is_redis_available():
        return
    get_redis_client().set(_cache_key(volunteer_id), status, ex=30)

def invalidate_volunteer_cache(volunteer_id: int) -> None:
    if not is_redis_available():
        return
    get_redis_client().delete(_cache_key(volunteer_id))

def _is_volunteer_available(volunteer_id: int, db: Session) -> bool:
    """Cache-Aside: Redis first, DB on miss, populate cache."""
    if not is_redis_available():
        from app.models.volunteer import Volunteer
        v = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
        return v.availability_status == "available" if v else False

    cached = get_redis_client().get(_cache_key(volunteer_id))
    if cached is not None:
        value = cached.decode() if isinstance(cached, bytes) else cached
        return value == "available"

    # cache miss — check DB
    from app.models.volunteer import Volunteer
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        return False

    set_volunteer_cache(volunteer_id, volunteer.availability_status)
    return volunteer.availability_status == "available"

# ── Blacklist checks ─────────────────────────────────────────────

def is_volunteer_blacklisted(volunteer_id: int, incident_id: int) -> bool:
    """
    Returns True if volunteer declined or timed out on this incident.
    Both declined and timedout volunteers are skipped.
    """
    if not is_redis_available():
        return False
    redis = get_redis_client()
    declined = redis.exists(_unavailable_key(volunteer_id, incident_id))
    timedout = redis.exists(_timedout_key(volunteer_id, incident_id))
    return bool(declined or timedout)

def blacklist_volunteer_declined(
    volunteer_id: int,
    incident_id: int,
    unavailable_minutes: int
) -> None:
    """
    Called when volunteer declines.
    unavailable_minutes = 0 means offline (handled separately in route)
    unavailable_minutes > 0 means skip for that window
    """
    if not is_redis_available():
        return
    if unavailable_minutes > 0:
        ttl = unavailable_minutes * 60
        get_redis_client().set(
            _unavailable_key(volunteer_id, incident_id),
            "declined",
            ex=ttl
        )

def blacklist_volunteer_timedout(volunteer_id: int, incident_id: int) -> None:
    """Called when volunteer doesn't respond in 60s."""
    if not is_redis_available():
        return
    # timedout volunteers are skipped for 30 minutes
    get_redis_client().set(
        _timedout_key(volunteer_id, incident_id),
        "timedout",
        ex=1800  # 30 minutes
    )

# ── Distributed lock ─────────────────────────────────────────────

def _acquire_lock(volunteer_id: int, incident_id: int) -> bool:
    if not is_redis_available():
        return True
    result = get_redis_client().set(
        name=_lock_key(volunteer_id),
        value=str(incident_id),
        nx=True,
        ex=60
    )
    return result is not None

def release_lock(volunteer_id: int) -> None:
    if not is_redis_available():
        return
    get_redis_client().delete(_lock_key(volunteer_id))

def release_all_locks(volunteer_ids: list[int]) -> None:
    for vid in volunteer_ids:
        release_lock(vid)
        
def _acquire_incident_lock(incident_id: int) -> bool:
    """
    Prevent duplicate assignment jobs running simultaneously.
    Lock expires in 30s — enough time for one assignment attempt.
    """
    if not is_redis_available():
        return True
    key = f"incident:lock:{incident_id}"
    result = get_redis_client().set(
        name=key,
        value="1",
        nx=True,
        ex=30   # 30s — assignment should complete in this time
    )
    return result is not None

def release_incident_lock(incident_id: int) -> None:
    if not is_redis_available():
        return
    get_redis_client().delete(f"incident:lock:{incident_id}")


def mark_incident_enqueued(incident_id: int) -> None:
    """Mark incident as having an active assignment job."""
    if not is_redis_available():
        return
    # TTL is just a safety net in case worker crashes
    # Normal flow: explicitly released in assign_volunteer finally block
    get_redis_client().set(f"incident:enqueued:{incident_id}", "1", ex=120)

def unmark_incident_enqueued(incident_id: int) -> None:
    """Called in finally block of assign_volunteer."""
    if not is_redis_available():
        return
    get_redis_client().delete(f"incident:enqueued:{incident_id}")

def is_incident_enqueued(incident_id: int) -> bool:
    if not is_redis_available():
        return False
    return get_redis_client().exists(f"incident:enqueued:{incident_id}") == 1


# ── Core matching ────────────────────────────────────────────────

def find_next_volunteer(
    db: Session,
    incident_id: int,
    incident_type: str,
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    exclude_user_id: int | None = None
) -> dict | None:
    """
    Finds single best available volunteer for an incident.
    Excludes:
      - incident reporter (exclude_user_id)
      - volunteers who declined this incident
      - volunteers who timed out on this incident
      - volunteers currently locked (being assigned elsewhere)
    Returns single best match or None.
    """
    from app.repositories.volunteer_repository import VolunteerRepository

    required_skill = _get_required_skill(incident_type)
    repo = VolunteerRepository(db)

    # fetch buffer of candidates from PostGIS
    candidates = repo.find_available_near(
        latitude=latitude,
        longitude=longitude,
        skill=required_skill,
        radius_km=radius_km,
        limit=20,  # large buffer — many may be blacklisted
        exclude_user_id=exclude_user_id
    )

    if not candidates:
        return None

    for candidate in candidates:
        volunteer_id = candidate["volunteer_id"]

        # skip if declined or timed out on this incident
        if is_volunteer_blacklisted(volunteer_id, incident_id):
            continue

        # skip if not available (cache-aside check)
        if not _is_volunteer_available(volunteer_id, db):
            continue

        # try to acquire lock — atomic, prevents race condition
        if not _acquire_lock(volunteer_id, incident_id):
            continue

        # found a valid volunteer
        return candidate

    return None