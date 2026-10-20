from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.user import ExperienceLevel

class CandidateBase(BaseModel):
    username: str = Field(...)
    email: Optional[str] = Field(None)
    experience_years: int = Field(default=3, ge=0, le=40)
    experience_level: ExperienceLevel = ExperienceLevel.MID
    target_role: str = "Senior Backend Engineer (Python/FastAPI)"
    target_companies: List[str] = ["Google", "Amazon", "Uber", "Razorpay"]
    focus_areas: List[str] = ["FastAPI", "MySQL Internals", "Concurrency", "System Design"]

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    total_score: int
    interviews_completed: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
