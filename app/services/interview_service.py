from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.contracts.interview import InterviewSessionContract
from app.contracts.ai import AIEvaluationContract
from app.services.ai_service import ai_service
from app.models.session import InterviewSession, InterviewTurn, SessionStatus
from app.models.question import InterviewQuestion
from app.schemas.session import SessionResponse, TurnResponse
from app.core.events import event_dispatcher, SessionCreatedEvent, TurnEvaluatedEvent

class InterviewSessionDomainService(InterviewSessionContract):
    """
    Decoupled Domain Service for Mock Interview Orchestration.
    Coordinates candidate multi-turn sessions, persistence, and delegates to the AIEvaluationContract.
    """

    def __init__(self, ai_evaluator: Optional[AIEvaluationContract] = None):
        self._ai_evaluator = ai_evaluator or ai_service

    def set_ai_evaluator(self, ai_evaluator: AIEvaluationContract):
        """Allows swapping the AI evaluator dynamically at runtime."""
        self._ai_evaluator = ai_evaluator

    def create_session(
        self,
        candidate_id: Optional[int],
        session_title: str,
        experience_level: str,
        target_company: Optional[str],
        db: Session
    ) -> InterviewSession:
        session = InterviewSession(
            candidate_id=candidate_id,
            session_title=session_title,
            experience_level=experience_level.lower(),
            target_company=target_company,
            status=SessionStatus.ACTIVE
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Publish decoupled domain event
        event_dispatcher.publish(SessionCreatedEvent(
            session_id=session.id,
            experience_level=session.experience_level,
            target_company=session.target_company or "MNC"
        ))
        return session

    def get_session(self, session_id: int, db: Session) -> Optional[InterviewSession]:
        return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

    async def process_turn(
        self,
        session_id: int,
        question_id: Optional[int],
        candidate_response: Optional[str],
        candidate_code: Optional[str],
        candidate_sql: Optional[str],
        db: Session
    ) -> InterviewTurn:
        session = self.get_session(session_id, db)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        question = None
        if question_id:
            question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()

        q_title = question.title if question else "Technical Backend Grilling"
        q_scenario = question.scenario_text if question else "Analyze the backend architecture trade-offs."

        # Fetch previous turns for conversational state context
        previous_turns = (
            db.query(InterviewTurn)
            .filter(InterviewTurn.session_id == session.id)
            .order_by(InterviewTurn.turn_number.asc())
            .all()
        )
        turn_num = len(previous_turns) + 1
        prev_cross_q = []
        for pt in previous_turns:
            prev_cross_q.extend(pt.cross_questions_asked or [])

        # Sanitize and cap submission size to defend database against storage bloat
        clean_resp = (candidate_response or "")[:50000]
        clean_code = (candidate_code or "")[:50000]
        clean_sql = (candidate_sql or "")[:20000]

        # Call AI Evaluation via decoupled contract
        eval_result = await self._ai_evaluator.evaluate_candidate_turn(
            question_title=q_title,
            scenario_text=q_scenario,
            experience_level=session.experience_level,
            target_company=session.target_company or "Top Tech MNC",
            candidate_response=clean_resp,
            candidate_code=clean_code,
            candidate_sql=clean_sql,
            previous_cross_questions=prev_cross_q
        )

        turn = InterviewTurn(
            session_id=session.id,
            turn_number=turn_num,
            question_id=question_id,
            interviewer_prompt=f"MNC Interview Round for {session.target_company} ({session.experience_level.upper()} Track)",
            candidate_response=clean_resp,
            candidate_code=clean_code,
            feedback=eval_result.get("feedback", "Good start."),
            score=eval_result.get("score", 7.0),
            cross_questions_asked=eval_result.get("cross_questions", []),
            key_strengths=eval_result.get("key_strengths", []),
            improvement_areas=eval_result.get("improvement_areas", [])
        )
        db.add(turn)

        # Update overall session score average
        all_scores = [t.score for t in previous_turns if t.score is not None] + [eval_result.get("score", 7.0)]
        session.overall_score = round(sum(all_scores) / len(all_scores), 1)

        db.commit()
        db.refresh(turn)

        # Publish decoupled domain event
        event_dispatcher.publish(TurnEvaluatedEvent(
            session_id=session.id,
            question_id=question_id or 0,
            score=turn.score,
            verdict="HIRE" if turn.score >= 7.0 else "REVIEW"
        ))

        return turn

    async def query_copilot(
        self,
        question_id: int,
        prompt_type: str,
        user_prompt: Optional[str],
        candidate_code: Optional[str],
        candidate_sql: Optional[str],
        session_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        exp_level = "mid"
        target_company = "Top Tech MNC"
        if session_id:
            session = self.get_session(session_id, db)
            if session:
                exp_level = session.experience_level
                target_company = session.target_company or "Top Tech MNC"

        return await self._ai_evaluator.query_copilot(
            question=question,
            prompt_type=prompt_type,
            user_prompt=user_prompt,
            candidate_code=candidate_code,
            candidate_sql=candidate_sql,
            experience_level=exp_level,
            target_company=target_company
        )

# Default singleton instance
interview_service = InterviewSessionDomainService()

