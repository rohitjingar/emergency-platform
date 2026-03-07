from sqlalchemy.orm import Session
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate
from app.models.incident import Incident
from app.core.exceptions import IncidentNotFoundError

def create_incident(db: Session, data: IncidentCreate, user_id: int) -> Incident:
    repo = IncidentRepository(db)
    return repo.create(
        type=data.type,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        priority=data.priority or "medium",
        user_id=user_id
    )

def get_incidents(db: Session, skip: int = 0, limit: int = 10) -> list[Incident]:
    repo = IncidentRepository(db)
    return repo.get_all(skip=skip, limit=limit)

def delete_incident(db: Session, incident_id: int) -> None:
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise IncidentNotFoundError(incident_id)
    repo.delete(incident)