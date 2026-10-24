from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.container import get_interview_service
from app.contracts.interview import InterviewSessionContract
from app.schemas.session import SessionCreate, SessionResponse, TurnCreate, TurnResponse, CopilotQueryRequest, CopilotQueryResponse
from app.core.security import get_optional_current_user
from app.models.user import Candidate

router = APIRouter(prefix="/interview", tags=["AI Mock Interview"])

@router.post("/sessions", response_model=SessionResponse)
def create_interview_session(
    payload: SessionCreate,
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    interview_svc: InterviewSessionContract = Depends(get_interview_service)
):
    """Initializes a new mock interview session with candidate calibration."""
    cand_id = payload.candidate_id or (current_user.id if current_user else None)
    return interview_svc.create_session(
        candidate_id=cand_id,
        session_title=payload.session_title,
        experience_level=payload.experience_level,
        target_company=payload.target_company,
        db=db
    )

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    interview_svc: InterviewSessionContract = Depends(get_interview_service)
):
    """Retrieves session state, turn history, and overall rating."""
    session = interview_svc.get_session(session_id, db=db)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session

@router.post("/turns", response_model=TurnResponse)
async def submit_interview_turn(
    payload: TurnCreate,
    db: Session = Depends(get_db),
    interview_svc: InterviewSessionContract = Depends(get_interview_service)
):
    """Processes candidate answer with AI Bar Raiser evaluation and follow-up generation."""
    return await interview_svc.process_turn(
        session_id=payload.session_id,
        question_id=payload.question_id,
        candidate_response=payload.candidate_response,
        candidate_code=payload.candidate_code,
        candidate_sql=payload.candidate_sql,
        db=db
    )

@router.post("/copilot", response_model=CopilotQueryResponse)
async def query_ai_copilot(
    payload: CopilotQueryRequest,
    db: Session = Depends(get_db),
    interview_svc: InterviewSessionContract = Depends(get_interview_service)
):
    """Interactive AI Copilot providing ELI5 explanations, architectural hints, complexity profiling, and coaching."""
    return await interview_svc.query_copilot(
        question_id=payload.question_id,
        prompt_type=payload.prompt_type,
        user_prompt=payload.user_prompt,
        candidate_code=payload.candidate_code,
        candidate_sql=payload.candidate_sql,
        session_id=payload.session_id,
        db=db
    )

