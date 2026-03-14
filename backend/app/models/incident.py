# models/incident.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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
    # ── Triage results (filled by agent after creation)
    severity = Column(String, nullable=True)        # Critical/High/Medium/Low
    confidence = Column(Float, nullable=True)        # 0.0 - 1.0
    reasoning = Column(String, nullable=True)        # why this severity
    rag_used = Column(String, nullable=True)         # "yes" / "no"