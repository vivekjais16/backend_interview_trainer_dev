from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.session import InterviewSession, InterviewTurn, SessionStatus
from app.models.question import InterviewQuestion
from app.schemas.session import SessionCreate, SessionResponse, TurnCreate, TurnResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/interview", tags=["AI Mock Interview"])

@router.post("/sessions", response_model=SessionResponse)
def create_interview_session(payload: SessionCreate, db: Session = Depends(get_db)):
    session = InterviewSession(
        candidate_id=payload.candidate_id,
        session_title=payload.session_title,
        experience_level=payload.experience_level.lower(),
        target_company=payload.target_company,
        status=SessionStatus.ACTIVE
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session

@router.post("/turns", response_model=TurnResponse)
async def submit_interview_turn(payload: TurnCreate, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    question = None
    if payload.question_id:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == payload.question_id).first()

    q_title = question.title if question else "Technical Backend Grilling"
    q_scenario = question.scenario_text if question else "Analyze the backend architecture trade-offs."

    # Fetch previous turns for context
    previous_turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == session.id).order_by(InterviewTurn.turn_number.asc()).all()
    turn_num = len(previous_turns) + 1
    prev_cross_q = []
    for pt in previous_turns:
        prev_cross_q.extend(pt.cross_questions_asked or [])

    # AI Evaluation & Deep Cross-Questioning
    eval_result = await ai_service.evaluate_candidate_turn(
        question_title=q_title,
        scenario_text=q_scenario,
        experience_level=session.experience_level,
        target_company=session.target_company,
        candidate_response=payload.candidate_response,
        candidate_code=payload.candidate_code,
        candidate_sql=payload.candidate_sql,
        previous_cross_questions=prev_cross_q
    )

    turn = InterviewTurn(
        session_id=session.id,
        turn_number=turn_num,
        question_id=payload.question_id,
        interviewer_prompt=f"MNC Interview Round for {session.target_company} ({session.experience_level.upper()} Track)",
        candidate_response=payload.candidate_response,
        candidate_code=payload.candidate_code,
        candidate_sql=payload.candidate_sql,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        cross_questions_asked=eval_result["cross_questions"],
        key_strengths=eval_result["key_strengths"],
        improvement_areas=eval_result["improvement_areas"]
    )
    db.add(turn)

    # Update overall session score average
    all_scores = [t.score for t in previous_turns if t.score is not None] + [eval_result["score"]]
    session.overall_score = round(sum(all_scores) / len(all_scores), 1)
    
    db.commit()
    db.refresh(turn)
    return turn
