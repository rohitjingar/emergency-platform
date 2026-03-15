from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.models.incident import Incident
from app.models.volunteer import Volunteer         
from app.models.notification import Notification    
from app.models.user import User  
from app.services.matching_service import (
    find_next_volunteer,
    release_lock,
    unmark_incident_enqueued
)
from app.services.notification_service import (
    notify_volunteer_assigned,
    notify_affected_no_volunteer,
    notify_admin_no_volunteer
)

from app.services.matching_service import (
    _acquire_incident_lock,
    release_incident_lock
)

MAX_ATTEMPTS = 5

def assign_volunteer(incident_id: int) -> None:
    """
    Job 2 — finds next available volunteer for an incident.
    Called from:
      - process_incident (after triage)
      - decline route (after volunteer declines)
      - timeout_worker (after 60s no response)

    This is the single place where volunteer assignment happens.
    """
    # prevent duplicate jobs running simultaneously for same incident
    if not _acquire_incident_lock(incident_id):
        print(f"Skipping incident {incident_id} — assignment already in progress")
        return
    
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            print(f"ERROR: Incident {incident_id} not found in assignment worker")
            return

        # guard — only assign if in correct state
        if incident.status not in ("searching", "open"):
            print(
                f"Skipping assignment for incident {incident_id} "
                f"— status is {incident.status}"
            )
            return

        # check attempts limit
        if incident.assignment_attempts >= MAX_ATTEMPTS:
            _handle_no_volunteer(db, incident)
            return

        # find next volunteer
        volunteer_match = find_next_volunteer(
            db=db,
            incident_id=incident.id,
            incident_type=incident.type,
            latitude=incident.latitude,
            longitude=incident.longitude,
            exclude_user_id=incident.user_id
        )
        incident.last_attempted_at = datetime.now(timezone.utc)
        if not volunteer_match:
            # no volunteer found right now
            # increment attempts, stay in searching
            incident.assignment_attempts += 1
            incident.status = "searching"
            db.commit()
            print(
                f"No volunteer found for incident {incident_id} "
                f"(attempt {incident.assignment_attempts}/{MAX_ATTEMPTS})"
            )
            return

        # volunteer found
        volunteer_id = volunteer_match["volunteer_id"]
        volunteer = db.query(Volunteer).filter(
            Volunteer.id == volunteer_id
        ).first()

        # assign
        incident.assigned_volunteer_id = volunteer_id
        incident.status = "pending_assignment"
        incident.assigned_at = datetime.now(timezone.utc)
        incident.assignment_attempts += 1
        db.commit()
        db.refresh(incident)

        # release lock — volunteer is pending, lock no longer needed
        release_lock(volunteer_id)

        # notify volunteer
        notify_volunteer_assigned(
            db=db,
            volunteer_user_id=volunteer.user_id,
            incident_id=incident.id,
            incident_type=incident.type,
            severity=incident.severity or "High",
            distance_km=volunteer_match["distance_km"]
        )

        print(
            f"Incident {incident_id} → volunteer {volunteer_id} "
            f"({volunteer_match['distance_km']}km) — pending confirmation "
            f"(attempt {incident.assignment_attempts}/{MAX_ATTEMPTS})"
        )

    except Exception as e:
        print(f"ERROR in assign_volunteer {incident_id}: {e}")
    finally:
        release_incident_lock(incident_id)
        unmark_incident_enqueued(incident_id)
        db.close()

def _handle_no_volunteer(db, incident: Incident) -> None:
    """All attempts exhausted — mark failed, notify everyone."""
    incident.status = "failed"
    db.commit()

    notify_affected_no_volunteer(
        db=db,
        affected_user_id=incident.user_id,
        incident_id=incident.id
    )
    notify_admin_no_volunteer(
        db=db,
        incident_id=incident.id,
        incident_type=incident.type,
        severity=incident.severity or "Unknown"
    )
    print(
        f"Incident {incident.id} FAILED — "
        f"no volunteer after {MAX_ATTEMPTS} attempts"
    )