from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.models.user import Candidate
from app.schemas.user import (
    UserHistoryResponse, PersonalizedRecommendationsResponse,
    MCQAttemptCreate, MCQAttemptResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["Candidate Tracking & Progress"])

@router.get("/history", response_model=UserHistoryResponse)
def get_user_history(
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Returns candidate's full mock interview history, MCQ test attempts, and code runs."""
    candidate = current_user
    if not candidate and candidate_id:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        # Fallback to the first seeded or created candidate for guest demonstration
        candidate = db.query(Candidate).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in or create an account to view your progress history."
        )

    return UserService.get_user_history(candidate, db=db)

@router.get("/recommendations", response_model=PersonalizedRecommendationsResponse)
def get_personalized_recommendations(
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Generates personalized study plan, weak area identification, and recommended questions based on target companies and key skills."""
    candidate = current_user
    if not candidate and candidate_id:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        # Fallback to first candidate for demo
        candidate = db.query(Candidate).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in or create an account to view personalized recommendations."
        )

    return UserService.get_personalized_recommendations(candidate, db=db)

@router.post("/mcq-attempt", response_model=MCQAttemptResponse)
def record_mcq_attempt(
    payload: MCQAttemptCreate,
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Records an MCQ answer attempt to track accuracy and domain skill progress."""
    candidate_id = payload.candidate_id or (current_user.id if current_user else None)
    if not candidate_id:
        # Fallback to demo candidate or create guest
        demo = db.query(Candidate).first()
        if demo:
            candidate_id = demo.id
        else:
            raise HTTPException(status_code=400, detail="candidate_id required or user must be signed in.")

    return UserService.record_mcq_attempt(candidate_id, payload, db=db)
