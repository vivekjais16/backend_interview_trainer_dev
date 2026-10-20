import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)
    session_title = Column(String(255), default="Full-Stack Backend MNC Mock Interview")
    experience_level = Column(String(50), default="mid")
    target_company = Column(String(100), default="Top Tech MNC")
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    overall_score = Column(Float, default=0.0)
    summary_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan")

class InterviewTurn(Base):
    __tablename__ = "interview_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    turn_number = Column(Integer, default=1)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    
    interviewer_prompt = Column(Text, nullable=False)
    candidate_response = Column(Text, nullable=True)
    candidate_code = Column(Text, nullable=True)
    candidate_sql = Column(Text, nullable=True)
    
    score = Column(Float, nullable=True) # 0 to 10
    feedback = Column(Text, nullable=True)
    cross_questions_asked = Column(JSON, default=list)
    key_strengths = Column(JSON, default=list)
    improvement_areas = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=utc_now)

    session = relationship("InterviewSession", back_populates="turns")
