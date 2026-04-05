from app.repositories.volunteer_repository import VolunteerRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentCreateResponse
from app.services.incident_service import create_incident, get_incidents, delete_incident
from app.core.dependencies import get_current_user, require_role
from app.core.exceptions import AppException
from app.models.incident import Incident
from app.services.matching_service import release_lock

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentCreateResponse)
def create(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = create_incident(db, data, user_id=int(current_user["sub"]))
        return IncidentCreateResponse(
            incident=result["incident"],
            queued=result["queued"],
            message=(
                "Incident reported. Our team is finding the nearest volunteer."
                if result["queued"]
                else "Incident reported. Processing in progress."
            )
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    return get_incidents(db, skip=skip, limit=limit, user_id=user_id)

@router.get("/{incident_id}/status")
def get_incident_status(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "incident_id": incident.id,
        "status": incident.status,
        "severity": incident.severity,
        "confidence": incident.confidence,
        "assigned_volunteer_id": incident.assigned_volunteer_id,
        "assignment_attempts": incident.assignment_attempts,
        "fallback_used": incident.fallback_used 
    }

@router.delete("/{incident_id}")
def remove_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    try:
        delete_incident(db, incident_id)
        return {"message": f"Incident {incident_id} deleted"}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
