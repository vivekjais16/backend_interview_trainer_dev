from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.question import InterviewQuestion, QuestionCategory, QuestionDifficulty
from app.schemas.question import (
    QuestionSummary,
    QuestionDetail,
    MCQVerifyRequest,
    MCQVerifyResponse,
    MCQQuizItem,
)

router = APIRouter(prefix="/questions", tags=["Interview Questions"])

@router.get("/phases")
def get_roadmap_phases(db: Session = Depends(get_db)):
    """Returns the 3 career phases (Basic, Intermediate, Advanced) with statistics."""
    all_qs = db.query(InterviewQuestion).all()
    phases_meta = [
        {
            "id": "basic",
            "number": 1,
            "title": "Phase 1: Foundation (Basic)",
            "subtitle": "Core Python Memory, SQL Queries, HTTP/FastAPI & Container Basics",
            "yoe_range": "0 - 2 YOE (Junior / Associate)",
            "badge_color": "emerald",
            "topics": ["Python Internals", "SQL Basics", "FastAPI Validation", "Docker Basics"],
            "count": sum(1 for q in all_qs if (q.phase or "basic").lower() == "basic"),
        },
        {
            "id": "intermediate",
            "number": 2,
            "title": "Phase 2: Production Engineering (Intermediate)",
            "subtitle": "Async Event Loops, Redis Caching, NoSQL Indexes & Celery Queues",
            "yoe_range": "3 - 5 YOE (Mid-Level SDE II)",
            "badge_color": "blue",
            "topics": ["Asyncio", "Redis Stampede", "MongoDB ESR", "Celery & RabbitMQ", "SQLAlchemy N+1"],
            "count": sum(1 for q in all_qs if (q.phase or "").lower() == "intermediate"),
        },
        {
            "id": "advanced",
            "number": 3,
            "title": "Phase 3: High Scale & Architecture (Advanced)",
            "subtitle": "Distributed Locks, Gap Locks, Transactional Outbox & Zero-Downtime Deploys",
            "yoe_range": "6+ YOE (Senior / Staff / Lead)",
            "badge_color": "purple",
            "topics": ["MySQL Gap Locks", "Kafka Rebalancing", "Redis Distributed Lock", "Transactional Outbox", "K8s Probes"],
            "count": sum(1 for q in all_qs if (q.phase or "").lower() in ("advanced", "architect")),
        },
    ]
    return {
        "phases": phases_meta,
        "total_questions": len(all_qs)
    }

@router.get("/mcq-quiz", response_model=List[MCQQuizItem])
def get_mcq_quiz(
    phase: Optional[str] = Query(None, description="Filter quiz by phase: basic, intermediate, advanced"),
    category: Optional[QuestionCategory] = Query(None, description="Filter quiz by category"),
    db: Session = Depends(get_db)
):
    """Returns interactive MCQ quiz questions for the given phase or all phases."""
    query = db.query(InterviewQuestion).filter(InterviewQuestion.mcq_question.isnot(None))
    
    if phase:
        p_clean = phase.lower()
        if p_clean == "advanced":
            query = query.filter(or_(InterviewQuestion.phase == "advanced", InterviewQuestion.phase == "architect"))
        else:
            query = query.filter(InterviewQuestion.phase == p_clean)
            
    if category:
        query = query.filter(InterviewQuestion.category == category)
        
    questions = query.order_by(InterviewQuestion.frequency_score.desc(), InterviewQuestion.id.asc()).all()
    
    quiz_items = []
    for q in questions:
        if q.mcq_options and len(q.mcq_options) >= 2:
            quiz_items.append(
                MCQQuizItem(
                    id=q.id,
                    title=q.title,
                    slug=q.slug,
                    category=q.category,
                    difficulty=q.difficulty,
                    phase=q.phase or "basic",
                    company_tags=q.company_tags or [],
                    mcq_question=q.mcq_question,
                    mcq_options=q.mcq_options
                )
            )
    return quiz_items

@router.post("/verify-mcq", response_model=MCQVerifyResponse)
def verify_mcq_answer(payload: MCQVerifyRequest, db: Session = Depends(get_db)):
    """Verifies a candidate's MCQ option selection and provides instant educational explanation."""
    q = db.query(InterviewQuestion).filter(InterviewQuestion.id == payload.question_id).first()
    if not q or not q.mcq_options:
        raise HTTPException(status_code=404, detail="Question or MCQ not found")
        
    is_correct = (payload.selected_index == q.mcq_correct_index)
    explanation = q.mcq_explanation or (q.theory_explanation[:400] if q.theory_explanation else "No explanation available.")
    
    return MCQVerifyResponse(
        is_correct=is_correct,
        correct_index=q.mcq_correct_index,
        explanation=explanation,
        question_id=q.id
    )

@router.get("", response_model=List[QuestionSummary])
def list_questions(
    phase: Optional[str] = Query(None, description="Filter by phase: basic, intermediate, advanced"),
    experience_years: Optional[int] = Query(None, ge=0, le=40, description="Filter by candidate years of experience"),
    experience_level: Optional[str] = Query(None, description="junior (0-2), mid (3-5), senior (6-9), lead (10+)"),
    category: Optional[QuestionCategory] = Query(None, description="Filter by topic category"),
    difficulty: Optional[QuestionDifficulty] = Query(None, description="Filter by difficulty"),
    company: Optional[str] = Query(None, description="Filter by MNC company name (e.g. Amazon, Google, Uber)"),
    search: Optional[str] = Query(None, description="Search query in title or scenario"),
    db: Session = Depends(get_db)
):
    query = db.query(InterviewQuestion)

    # Phase filtering
    if phase:
        p_clean = phase.lower()
        if p_clean == "advanced":
            query = query.filter(or_(InterviewQuestion.phase == "advanced", InterviewQuestion.phase == "architect"))
        else:
            query = query.filter(InterviewQuestion.phase == p_clean)

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

    # Convert to QuestionSummary with has_mcq populated
    summaries = []
    for q in questions:
        summaries.append(
            QuestionSummary(
                id=q.id,
                title=q.title,
                slug=q.slug,
                category=q.category,
                difficulty=q.difficulty,
                min_exp_years=q.min_exp_years,
                max_exp_years=q.max_exp_years,
                company_tags=q.company_tags or [],
                frequency_score=q.frequency_score,
                mindmap_topic=q.mindmap_topic,
                has_python_sandbox=bool(q.has_python_sandbox),
                has_sql_sandbox=bool(q.has_sql_sandbox),
                has_redis_sandbox=bool(q.has_redis_sandbox),
                has_nosql_sandbox=bool(q.has_nosql_sandbox),
                phase=q.phase or "basic",
                has_mcq=bool(q.mcq_question and q.mcq_options and len(q.mcq_options) >= 2)
            )
        )
    return summaries

@router.get("/{id_or_slug}", response_model=QuestionDetail)
def get_question(id_or_slug: str, db: Session = Depends(get_db)):
    if id_or_slug.isdigit():
        q = db.query(InterviewQuestion).filter(InterviewQuestion.id == int(id_or_slug)).first()
    else:
        q = db.query(InterviewQuestion).filter(InterviewQuestion.slug == id_or_slug).first()

    if not q:
        raise HTTPException(status_code=404, detail="Interview question not found")
    return q
