from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True