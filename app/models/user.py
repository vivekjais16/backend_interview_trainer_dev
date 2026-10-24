import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Boolean, ForeignKey
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
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(150), nullable=True)
    experience_years = Column(Integer, default=2)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.MID, index=True)
    target_role = Column(String(150), default="Senior Backend Engineer (Python/FastAPI)")
    target_companies = Column(JSON, default=list) # e.g. ["Google", "Amazon", "Uber", "Meta", "Stripe"]
    key_skills = Column(JSON, default=list)       # e.g. ["Python", "FastAPI", "SQL", "Docker", "Redis", "Distributed Systems"]
    focus_areas = Column(JSON, default=list)      # e.g. ["Concurrency", "System Design", "Database Indexing"]
    total_score = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class UserMCQAttempt(Base):
    __tablename__ = "user_mcq_attempts"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    question_slug = Column(String(150), nullable=True, index=True)
    domain = Column(String(100), nullable=True, index=True)
    selected_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, default=False)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
