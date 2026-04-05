from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="open")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String, nullable=True)       
    confidence = Column(Float, nullable=True)       
    reasoning = Column(String, nullable=True)        
    rag_used = Column(String, nullable=True) 
    assigned_volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)        
    assignment_attempts = Column(Integer, default=0)
    last_attempted_at = Column(DateTime(timezone=True), nullable=True)
    fallback_used = Column(Boolean, default=False)                    