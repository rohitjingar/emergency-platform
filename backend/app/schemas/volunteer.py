from pydantic import BaseModel, field_validator
from typing import Optional

VALID_SKILLS = {"medical", "fire", "flood", "rescue"}
VALID_STATUSES = {"available", "busy", "offline"}

class VolunteerRegister(BaseModel):
    skills: list[str]
    radius_km: float = 10.0

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        invalid = set(v) - VALID_SKILLS
        if invalid:
            raise ValueError(f"Invalid skills: {invalid}. Valid: {VALID_SKILLS}")
        if not v:
            raise ValueError("At least one skill required")
        return v

    @field_validator("radius_km")
    @classmethod
    def validate_radius(cls, v):
        if v < 1 or v > 100:
            raise ValueError("radius_km must be between 1 and 100")
        return v

class VolunteerUpdateLocation(BaseModel):
    latitude: float
    longitude: float

class VolunteerUpdateStatus(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Valid: {VALID_STATUSES}")
        return v

class VolunteerResponse(BaseModel):
    id: int
    user_id: int
    skills: list[str]
    availability_status: str
    radius_km: float

    class Config:
        from_attributes = True

class VolunteerMatch(BaseModel):
    volunteer_id: int
    user_id: int
    skills: list[str]
    distance_meters: float
    distance_km: float
    
class VolunteerLocationResponse(BaseModel):
    id: int
    user_id: int
    skills: list[str]
    availability_status: str
    radius_km: float
    latitude: float
    longitude: float

    class Config:
        from_attributes = False  # we'll build this manually