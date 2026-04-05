from sqlalchemy.orm import Session
from app.models.incident import Incident

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        type: str,
        description: str,
        latitude: float,
        longitude: float,
        priority: str,
        user_id: int
    ) -> Incident:
        incident = Incident(
            type=type,
            description=description,
            latitude=latitude,
            longitude=longitude,
            priority=priority,
            user_id=user_id
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Incident]:
        return self.db.query(Incident).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 10) -> list[Incident]:
        return self.db.query(Incident).filter(
            Incident.user_id == user_id
        ).order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, incident_id: int) -> Incident | None:
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def delete(self, incident: Incident) -> None:
        self.db.delete(incident)
        self.db.commit()