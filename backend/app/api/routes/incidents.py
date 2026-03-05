from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.core.security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/incidents", tags=["Incidents"])
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload  # contains {"sub": user_id, "role": role}

@router.post("/", response_model=IncidentResponse)
def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    incident = Incident(
        type=data.type,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        priority=data.priority,
        user_id=int(current_user["sub"])
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/", response_model=List[IncidentResponse])
def get_incidents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Incident).offset(skip).limit(limit).all()