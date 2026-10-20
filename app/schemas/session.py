from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.session import SessionStatus

class TurnCreate(BaseModel):
    session_id: int
    question_id: Optional[int] = None
    candidate_response: Optional[str] = None
    candidate_code: Optional[str] = None
    candidate_sql: Optional[str] = None

class TurnResponse(BaseModel):
    id: int
    session_id: int
    turn_number: int
    question_id: Optional[int]
    interviewer_prompt: str
    candidate_response: Optional[str]
    candidate_code: Optional[str]
    candidate_sql: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    cross_questions_asked: List[str]
    key_strengths: List[str]
    improvement_areas: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    candidate_id: Optional[int] = None
    session_title: Optional[str] = "Full-Stack Backend MNC Mock Interview"
    experience_level: str = "mid" # junior, mid, senior, lead
    target_company: str = "Top Tech MNC"
    topic_category: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    candidate_id: Optional[int]
    session_title: str
    experience_level: str
    target_company: str
    status: SessionStatus
    overall_score: float
    summary_feedback: Optional[str]
    created_at: datetime
    updated_at: datetime
    turns: List[TurnResponse] = []

    model_config = ConfigDict(from_attributes=True)
