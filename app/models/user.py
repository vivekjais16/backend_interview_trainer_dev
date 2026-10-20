import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class ExperienceLevel(str, enum.Enum):
    JUNIOR = "junior"       # 0 - 2 Years
    MID = "mid"             # 3 - 5 Years
    SENIOR = "senior"       # 6 - 9 Years
    LEAD = "lead"           # 10+ Years / Architect

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    experience_years = Column(Integer, default=2)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.MID, index=True)
    target_role = Column(String(150), default="Senior Backend Engineer (Python/FastAPI)")
    target_companies = Column(JSON, default=list) # e.g. ["Google", "Amazon", "Uber", "Razorpay"]
    focus_areas = Column(JSON, default=list)      # e.g. ["FastAPI", "MySQL Internals", "Concurrency", "System Design"]
    total_score = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
