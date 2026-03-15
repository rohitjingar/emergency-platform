from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from app.db.database import Base

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    skills = Column(ARRAY(String), nullable=False, default=[])
    availability_status = Column(String, nullable=False, default="offline")
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    radius_km = Column(Float, default=10.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())