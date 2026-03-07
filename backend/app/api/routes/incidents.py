from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.services.incident_service import create_incident, get_incidents, delete_incident
from app.core.dependencies import get_current_user, require_role
from app.core.exceptions import AppException

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentResponse)
def create(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_incident(db, data, user_id=int(current_user["sub"]))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_incidents(db, skip=skip, limit=limit)

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