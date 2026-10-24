from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.models.user import ExperienceLevel

# Legacy backward-compatible schemas
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


# Enhanced User Accounts & Progress Schemas
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = None
    full_name: Optional[str] = None
    experience_years: int = Field(default=3, ge=0, le=40)
    experience_level: str = "mid" # junior, mid, senior, lead
    target_role: str = "Senior Backend Engineer (Python/FastAPI)"
    target_companies: List[str] = ["Google", "Amazon"]
    key_skills: List[str] = ["Python", "FastAPI", "SQL", "Docker", "Redis", "Distributed Systems"]

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str

class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    experience_years: Optional[int] = None
    experience_level: Optional[str] = None
    target_role: Optional[str] = None
    target_companies: Optional[List[str]] = None
    key_skills: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    experience_years: int
    experience_level: str
    target_role: str
    target_companies: List[str] = []
    key_skills: List[str] = []
    focus_areas: List[str] = []
    total_score: int
    interviews_completed: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MCQAttemptCreate(BaseModel):
    candidate_id: Optional[int] = None
    question_id: Optional[int] = None
    question_slug: Optional[str] = None
    domain: Optional[str] = "General"
    selected_index: int
    is_correct: bool
    time_spent_seconds: int = 0

class MCQAttemptResponse(BaseModel):
    id: int
    candidate_id: int
    question_id: Optional[int] = None
    question_slug: Optional[str] = None
    domain: Optional[str] = None
    selected_index: int
    is_correct: bool
    time_spent_seconds: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SkillAssessment(BaseModel):
    skill: str
    mastery_pct: int
    status: str # "mastered", "in_progress", "needs_practice", "untested"
    questions_tested: int
    correct_count: int

class PersonalizedRecommendationsResponse(BaseModel):
    candidate_id: int
    target_role: str
    target_companies: List[str]
    key_skills: List[str]
    overall_readiness_score: int # 0 to 100
    skills_breakdown: List[SkillAssessment]
    weak_areas: List[str]
    strengths: List[str]
    tailored_action_plan: List[str]
    recommended_questions: List[Dict[str, Any]]

class UserHistoryResponse(BaseModel):
    user: UserResponse
    mcq_attempts_count: int
    mcq_accuracy_pct: float
    interview_sessions_count: int
    average_interview_score: float
    recent_mcq_attempts: List[MCQAttemptResponse]
    recent_interview_sessions: List[Dict[str, Any]]
    recent_code_executions: List[Dict[str, Any]]
