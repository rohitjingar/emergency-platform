# app/api/routes/volunteers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.db.database import get_db
from app.schemas.volunteer import (
    VolunteerRegister, VolunteerUpdateLocation,
    VolunteerUpdateStatus, VolunteerResponse,
    VolunteerLocationResponse
)
from app.repositories.volunteer_repository import VolunteerRepository
from app.core.dependencies import get_current_user, require_role
from app.models.incident import Incident
from app.models.notification import Notification

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])

# ── Register / Location / Status (unchanged) ────────────────────

@router.post("/register", response_model=VolunteerResponse)
def register_volunteer(
    data: VolunteerRegister,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)
    existing = repo.get_by_user_id(user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already registered as volunteer")
    volunteer = repo.create(
        user_id=user_id,
        skills=data.skills,
        radius_km=data.radius_km
    )
    return volunteer

@router.patch("/location", response_model=VolunteerLocationResponse)
def update_location(
    data: VolunteerUpdateLocation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)
    volunteer = repo.get_by_user_id(user_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")
    return repo.update_location(volunteer, data.latitude, data.longitude)

@router.patch("/status", response_model=VolunteerResponse)
def update_status(
    data: VolunteerUpdateStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)
    volunteer = repo.get_by_user_id(user_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")
    return repo.update_status(volunteer, data.status)

@router.get("/available")
def get_available_volunteers(
    lat: float,
    lng: float,
    skill: str,
    radius_km: float = 10.0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = VolunteerRepository(db)
    results = repo.find_available_near(
        latitude=lat,
        longitude=lng,
        skill=skill,
        radius_km=radius_km,
        exclude_user_id=int(current_user["sub"])
    )
    return {"volunteers": results, "count": len(results)}

# ── My pending incidents ─────────────────────────────────────────

@router.get("/my-pending")
def get_my_pending_incidents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    """
    Volunteer polls this to see incidents assigned to them
    that are waiting for accept/decline.
    """
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)

    volunteer = repo.get_by_user_id(user_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")

    pending = db.query(Incident).filter(
        Incident.assigned_volunteer_id == volunteer.id,
        Incident.status == "pending_assignment"
    ).all()

    return {
        "pending_incidents": [
            {
                "incident_id": inc.id,
                "type": inc.type,
                "description": inc.description,
                "severity": inc.severity,
                "priority": inc.priority,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "assigned_at": inc.assigned_at,
            }
            for inc in pending
        ],
        "count": len(pending)
    }

# ── Accept ───────────────────────────────────────────────────────

@router.post("/incidents/{incident_id}/accept")
def accept_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)

    volunteer = repo.get_by_user_id(user_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")

    # verify this incident is actually assigned to this volunteer
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.assigned_volunteer_id == volunteer.id,
        Incident.status == "pending_assignment"
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found or not assigned to you or already handled."
        )

    # confirm assignment
    incident.status = "assigned"
    db.commit()
    db.refresh(incident)

    # volunteer is now responding — update status
    repo.update_status(volunteer, "responding")

    # notify affected user that help is coming
    from app.services.notification_service import notify_affected_user_assigned
    # find distance for notification message
    from app.services.matching_service import find_next_volunteer
    notify_affected_user_assigned(
        db=db,
        affected_user_id=incident.user_id,
        incident_id=incident.id,
        volunteer_user_id=volunteer.user_id,
        distance_km=0.0  # we don't recalculate here — good enough for notification
    )

    return {
        "message": "Incident accepted. Please proceed to the location.",
        "incident_id": incident_id,
        "type": incident.type,
        "severity": incident.severity,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "status": "assigned"
    }

# ── Decline ──────────────────────────────────────────────────────

class DeclineRequest(BaseModel):
    unavailable_minutes: int

    @field_validator("unavailable_minutes")
    @classmethod
    def validate_minutes(cls, v):
        if v not in [0, 30, 60, 120]:
            raise ValueError("unavailable_minutes must be 0, 30, 60, or 120")
        return v

@router.post("/incidents/{incident_id}/decline")
def decline_incident(
    incident_id: int,
    data: DeclineRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["volunteer"]))
):
    user_id = int(current_user["sub"])
    repo = VolunteerRepository(db)

    volunteer = repo.get_by_user_id(user_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")

    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.assigned_volunteer_id == volunteer.id,
        Incident.status == "pending_assignment"
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found or not assigned to you."
        )

    from app.services.matching_service import blacklist_volunteer_declined
    from app.services.notification_service import notify_volunteer_please_go_offline
    from app.workers.queues import assignment_queue
    from app.workers.assignment_worker import assign_volunteer

    # blacklist this volunteer for this incident
    blacklist_volunteer_declined(
        volunteer_id=volunteer.id,
        incident_id=incident.id,
        unavailable_minutes=data.unavailable_minutes
    )

    # handle indefinite unavailability
    if data.unavailable_minutes == 0:
        repo.update_status(volunteer, "offline")
        notify_volunteer_please_go_offline(
            db=db,
            volunteer_user_id=volunteer.user_id
        )
        unavailable_message = "You have been set to offline."
    else:
        unavailable_message = (
            f"You will be skipped for {data.unavailable_minutes} minutes."
        )

    # reset incident
    incident.assigned_volunteer_id = None
    incident.assigned_at = None
    incident.status = "searching"
    db.commit()

    # enqueue Job 2 — non-blocking, returns instantly
    assignment_queue.enqueue(
        assign_volunteer,
        incident.id,
        job_timeout=120
    )

    # API returns immediately
    return {
        "message": f"Declined. {unavailable_message} Finding next volunteer.",
        "incident_id": incident_id,
        "unavailable_minutes": data.unavailable_minutes
    }