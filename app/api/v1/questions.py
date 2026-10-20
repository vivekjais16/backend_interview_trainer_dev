from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.question import InterviewQuestion, QuestionCategory, QuestionDifficulty
from app.schemas.question import QuestionSummary, QuestionDetail

router = APIRouter(prefix="/questions", tags=["Interview Questions"])

@router.get("", response_model=List[QuestionSummary])
def list_questions(
    experience_years: Optional[int] = Query(None, ge=0, le=40, description="Filter by candidate years of experience"),
    experience_level: Optional[str] = Query(None, description="junior (0-2), mid (3-5), senior (6-9), lead (10+)"),
    category: Optional[QuestionCategory] = Query(None, description="Filter by topic category"),
    difficulty: Optional[QuestionDifficulty] = Query(None, description="Filter by difficulty"),
    company: Optional[str] = Query(None, description="Filter by MNC company name (e.g. Amazon, Google, Uber)"),
    search: Optional[str] = Query(None, description="Search query in title or scenario"),
    db: Session = Depends(get_db)
):
    query = db.query(InterviewQuestion)

    # Experience level mapping
    if experience_years is not None:
        query = query.filter(
            InterviewQuestion.min_exp_years <= experience_years,
            InterviewQuestion.max_exp_years >= experience_years
        )
    elif experience_level:
        lvl = experience_level.lower()
        if lvl == "junior":
            query = query.filter(InterviewQuestion.min_exp_years <= 2, InterviewQuestion.max_exp_years >= 0)
        elif lvl == "mid":
            query = query.filter(InterviewQuestion.min_exp_years <= 5, InterviewQuestion.max_exp_years >= 3)
        elif lvl == "senior":
            query = query.filter(InterviewQuestion.min_exp_years <= 9, InterviewQuestion.max_exp_years >= 6)
        elif lvl == "lead":
            query = query.filter(InterviewQuestion.min_exp_years >= 10)

    if category:
        query = query.filter(InterviewQuestion.category == category)
    if difficulty:
        query = query.filter(InterviewQuestion.difficulty == difficulty)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                InterviewQuestion.title.ilike(search_fmt),
                InterviewQuestion.scenario_text.ilike(search_fmt)
            )
        )

    questions = query.order_by(InterviewQuestion.frequency_score.desc(), InterviewQuestion.id.asc()).all()

    if company:
        comp_lower = company.lower()
        questions = [
            q for q in questions 
            if any(comp_lower in str(tag).lower() for tag in (q.company_tags or []))
        ]

    return questions

@router.get("/{id_or_slug}", response_model=QuestionDetail)
def get_question(id_or_slug: str, db: Session = Depends(get_db)):
    if id_or_slug.isdigit():
        q = db.query(InterviewQuestion).filter(InterviewQuestion.id == int(id_or_slug)).first()
    else:
        q = db.query(InterviewQuestion).filter(InterviewQuestion.slug == id_or_slug).first()

    if not q:
        raise HTTPException(status_code=404, detail="Interview question not found")
    return q
