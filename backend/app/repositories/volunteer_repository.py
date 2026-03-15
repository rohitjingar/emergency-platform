from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.volunteer import Volunteer
from datetime import datetime, timezone
from app.services.matching_service import set_volunteer_cache

class VolunteerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, skills: list[str], radius_km: float = 10.0) -> Volunteer:
        volunteer = Volunteer(
            user_id=user_id,
            skills=skills,
            availability_status="available",
            radius_km=radius_km
        )
        self.db.add(volunteer)
        self.db.commit()
        self.db.refresh(volunteer)
        return volunteer

    def get_by_user_id(self, user_id: int) -> Volunteer | None:
        return self.db.query(Volunteer).filter(
            Volunteer.user_id == user_id
        ).first()

    def update_location(self, volunteer: Volunteer, latitude: float, longitude: float) -> dict:
        volunteer.location = f"SRID=4326;POINT({longitude} {latitude})"
        volunteer.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(volunteer)
        return {
            "id": volunteer.id,
            "user_id": volunteer.user_id,
            "skills": volunteer.skills,
            "availability_status": volunteer.availability_status,
            "radius_km": volunteer.radius_km,
            "latitude": latitude,
            "longitude": longitude
        }

    def update_status(self, volunteer: Volunteer, status: str) -> Volunteer:

        volunteer.availability_status = status
        volunteer.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(volunteer)

        # always cache real status — available, busy, or offline
        set_volunteer_cache(volunteer.id, status)

        return volunteer

    def find_available_near(
        self,
        latitude: float,
        longitude: float,
        skill: str,
        radius_km: float = 10.0,
        limit: int = 3,
        exclude_user_id: int | None = None
    ) -> list[dict]:
        """
        Core geo query — finds nearest available volunteers.
        Uses both indexes: btree on availability + GIST on location.
        Returns list of dicts with volunteer + distance.
        """
        radius_meters = radius_km * 1000

        sql = text("""
            SELECT 
                v.id,
                v.user_id,
                v.skills,
                v.availability_status,
                v.radius_km,
                ROUND(
                    ST_Distance(
                        v.location,
                        ST_Point(:longitude, :latitude)::geography
                    )::numeric
                ) as distance_meters
            FROM volunteers v
            WHERE 
                v.availability_status = 'available'
                AND v.location IS NOT NULL
                AND :skill = ANY(v.skills)
                AND ST_DWithin(
                    v.location,
                    ST_Point(:longitude, :latitude)::geography,
                    :radius_meters
                )
                AND (:exclude_user_id IS NULL OR v.user_id != :exclude_user_id)
            ORDER BY distance_meters ASC
            LIMIT :limit
        """)

        result = self.db.execute(sql, {
            "latitude": latitude,
            "longitude": longitude,
            "skill": skill,
            "radius_meters": radius_meters,
            "limit": limit,
            "exclude_user_id": exclude_user_id 
        })

        rows = result.fetchall()
        return [
            {
                "volunteer_id": row.id,
                "user_id": row.user_id,
                "skills": row.skills,
                "availability_status": row.availability_status,
                "distance_meters": row.distance_meters,
                "distance_km": round(row.distance_meters / 1000, 2)
            }
            for row in rows
        ]