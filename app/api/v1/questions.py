from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.container import get_question_service
from app.contracts.questions import QuestionServiceContract
from app.models.question import QuestionDifficulty
from app.schemas.question import (
    QuestionSummary,
    QuestionDetail,
    MCQVerifyRequest,
    MCQVerifyResponse,
    MCQQuizItem,
)

from app.core.security import get_optional_current_user
from app.models.user import Candidate, UserMCQAttempt

router = APIRouter(prefix="/questions", tags=["Interview Questions"])

@router.get("/phases")
def get_roadmap_phases(
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Returns the 3 career phases (Basic, Intermediate, Advanced) with statistics."""
    return q_service.get_phases(db)

@router.get("/mcq-quiz", response_model=List[MCQQuizItem])
def get_mcq_quiz(
    phase: Optional[str] = Query(None, description="Filter quiz by phase: basic, intermediate, advanced"),
    category: Optional[str] = Query(None, description="Filter quiz by category"),
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Returns interactive MCQ quiz questions for the given phase or all phases."""
    return q_service.get_mcq_quiz(phase=phase, db=db)

@router.post("/verify-mcq", response_model=MCQVerifyResponse)
def verify_mcq_answer(
    payload: MCQVerifyRequest,
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Verifies a candidate's MCQ option selection and provides instant educational explanation."""
    res = q_service.verify_mcq(question_id=payload.question_id, selected_index=payload.selected_index, db=db)
    if not res:
        raise HTTPException(status_code=404, detail="Question or MCQ not found")

    if current_user:
        try:
            attempt = UserMCQAttempt(
                candidate_id=current_user.id,
                question_id=payload.question_id,
                selected_index=payload.selected_index,
                is_correct=res.is_correct
            )
            db.add(attempt)
            if res.is_correct:
                current_user.total_score = (current_user.total_score or 0) + 10
            db.commit()
        except Exception:
            pass

    return res

@router.get("/most-asked", response_model=List[QuestionSummary])
def get_most_asked_questions(
    limit: int = Query(50, ge=1, le=200, description="Max questions to return"),
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Returns top high-frequency most-asked MNC interview questions."""
    return q_service.get_most_asked_questions(limit=limit, db=db)

@router.get("/concepts")
def get_centralized_concepts(
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Returns centralized InterviewBit and GeeksforGeeks master concept cheat sheets."""
    return q_service.get_concepts()

@router.get("", response_model=List[QuestionSummary])
def list_questions(
    phase: Optional[str] = Query(None, description="Filter by phase: basic, intermediate, advanced"),
    experience_years: Optional[int] = Query(None, ge=0, le=40, description="Filter by candidate years of experience"),
    experience_level: Optional[str] = Query(None, description="junior (0-2), mid (3-5), senior (6-9), lead (10+)"),
    category: Optional[str] = Query(None, description="Filter by topic category"),
    difficulty: Optional[QuestionDifficulty] = Query(None, description="Filter by difficulty"),
    company: Optional[str] = Query(None, description="Filter by MNC company name (e.g. Amazon, Google, Uber)"),
    search: Optional[str] = Query(None, description="Search query in title or scenario"),
    most_asked: Optional[bool] = Query(None, description="Filter for top frequency most asked questions"),
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Lists questions with adaptive experience calibration and domain category filtering."""
    return q_service.list_questions(
        phase=phase,
        experience_years=experience_years,
        experience_level=experience_level,
        category=category,
        difficulty=difficulty,
        company=company,
        search=search,
        most_asked=most_asked,
        db=db
    )

@router.get("/{id_or_slug}", response_model=QuestionDetail)
def get_question(
    id_or_slug: str,
    db: Session = Depends(get_db),
    q_service: QuestionServiceContract = Depends(get_question_service)
):
    """Retrieves deep question specification, theory breakdown, and starter sandbox templates."""
    q = q_service.get_question(id_or_slug, db=db)
    if not q:
        raise HTTPException(status_code=404, detail="Interview question not found")
    return q
