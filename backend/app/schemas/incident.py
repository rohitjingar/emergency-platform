from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentCreate(BaseModel):
    type: str
    description: str
    latitude: float
    longitude: float
    priority: Optional[str] = "medium"

class IncidentResponse(BaseModel):
    id: int
    type: str
    description: str
    latitude: float
    longitude: float
    priority: str
    status: str
    severity: Optional[str] = None
    confidence: Optional[float] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
class TriageResult(BaseModel):
    severity: Optional[str]
    confidence: Optional[float]
    reasoning: Optional[str]
    rag_used: Optional[bool]
    processing_ms: int
        
        
class MatchedVolunteer(BaseModel):
    volunteer_id: int
    user_id: int
    skills: list[str]
    distance_meters: float
    distance_km: float

class IncidentCreateResponse(BaseModel):
    incident: IncidentResponse
    queued: bool
    message: str

    class Config:
        from_attributes = True