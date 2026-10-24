import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.user import Candidate, ExperienceLevel, UserMCQAttempt
from app.models.session import InterviewSession, InterviewTurn
from app.models.execution import ExecutionLog
from app.models.question import InterviewQuestion
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserProfileUpdateRequest,
    UserResponse, AuthTokenResponse, MCQAttemptCreate, MCQAttemptResponse,
    UserHistoryResponse, PersonalizedRecommendationsResponse, SkillAssessment
)

logger = logging.getLogger(__name__)

class UserService:
    """Service managing user authentication, progress tracking, history, and AI-personalized guidance."""

    @staticmethod
    def register_user(payload: UserRegisterRequest, db: Session) -> AuthTokenResponse:
        existing = db.query(Candidate).filter(
            (Candidate.username == payload.username) | 
            (Candidate.email == payload.email if payload.email else False)
        ).first()
        if existing:
            if existing.username == payload.username:
                raise ValueError("Username is already taken. Please choose another username.")
            if payload.email and existing.email == payload.email:
                raise ValueError("Email is already registered. Please sign in or use another email.")

        try:
            exp_lvl = ExperienceLevel(payload.experience_level.lower())
        except Exception:
            exp_lvl = ExperienceLevel.MID

        candidate = Candidate(
            username=payload.username.strip(),
            email=payload.email.strip() if payload.email else None,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name.strip() if payload.full_name else payload.username.strip(),
            experience_years=payload.experience_years,
            experience_level=exp_lvl,
            target_role=payload.target_role,
            target_companies=payload.target_companies or ["Google", "Amazon"],
            key_skills=payload.key_skills or ["Python", "FastAPI", "SQL", "Docker", "Redis", "Distributed Systems"],
            focus_areas=payload.key_skills or ["Concurrency", "System Design"],
            total_score=0,
            interviews_completed=0
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        token = create_access_token({"sub": str(candidate.id), "username": candidate.username})
        return AuthTokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(candidate)
        )

    @staticmethod
    def authenticate_user(payload: UserLoginRequest, db: Session) -> AuthTokenResponse:
        identifier = payload.username_or_email.strip()
        candidate = db.query(Candidate).filter(
            (Candidate.username == identifier) | (Candidate.email == identifier)
        ).first()

        if not candidate or not verify_password(payload.password, candidate.hashed_password):
            raise ValueError("Invalid username/email or password.")

        token = create_access_token({"sub": str(candidate.id), "username": candidate.username})
        return AuthTokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(candidate)
        )

    @staticmethod
    def update_profile(candidate: Candidate, payload: UserProfileUpdateRequest, db: Session) -> UserResponse:
        if payload.full_name is not None:
            candidate.full_name = payload.full_name.strip()
        if payload.email is not None:
            candidate.email = payload.email.strip()
        if payload.experience_years is not None:
            candidate.experience_years = payload.experience_years
        if payload.experience_level is not None:
            try:
                candidate.experience_level = ExperienceLevel(payload.experience_level.lower())
            except Exception:
                pass
        if payload.target_role is not None:
            candidate.target_role = payload.target_role.strip()
        if payload.target_companies is not None:
            candidate.target_companies = payload.target_companies
        if payload.key_skills is not None:
            candidate.key_skills = payload.key_skills
        if payload.focus_areas is not None:
            candidate.focus_areas = payload.focus_areas

        db.commit()
        db.refresh(candidate)
        return UserResponse.model_validate(candidate)

    @staticmethod
    def record_mcq_attempt(candidate_id: int, payload: MCQAttemptCreate, db: Session) -> MCQAttemptResponse:
        attempt = UserMCQAttempt(
            candidate_id=candidate_id,
            question_id=payload.question_id,
            question_slug=payload.question_slug,
            domain=payload.domain or "General",
            selected_index=payload.selected_index,
            is_correct=payload.is_correct,
            time_spent_seconds=payload.time_spent_seconds
        )
        db.add(attempt)
        
        # Increment candidate total_score if correct
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if candidate and payload.is_correct:
            candidate.total_score = (candidate.total_score or 0) + 10

        db.commit()
        db.refresh(attempt)
        return MCQAttemptResponse.model_validate(attempt)

    @staticmethod
    def get_user_history(candidate: Candidate, db: Session) -> UserHistoryResponse:
        # MCQ Stats
        mcq_attempts = db.query(UserMCQAttempt).filter(
            UserMCQAttempt.candidate_id == candidate.id
        ).order_by(desc(UserMCQAttempt.created_at)).all()

        total_mcqs = len(mcq_attempts)
        correct_mcqs = sum(1 for a in mcq_attempts if a.is_correct)
        accuracy_pct = round((correct_mcqs / total_mcqs * 100), 1) if total_mcqs > 0 else 0.0

        # Interview Sessions
        sessions = db.query(InterviewSession).filter(
            InterviewSession.candidate_id == candidate.id
        ).order_by(desc(InterviewSession.created_at)).all()

        total_sessions = len(sessions)
        avg_score = round(sum(s.overall_score for s in sessions) / total_sessions, 1) if total_sessions > 0 else 0.0

        # Code executions
        code_runs = db.query(ExecutionLog).filter(
            ExecutionLog.candidate_id == candidate.id
        ).order_by(desc(ExecutionLog.created_at)).limit(10).all()

        formatted_sessions = []
        for s in sessions[:15]:
            turns_summary = [{
                "turn_number": t.turn_number,
                "score": t.score,
                "interviewer_prompt": t.interviewer_prompt[:80] + "..." if len(t.interviewer_prompt) > 80 else t.interviewer_prompt,
                "key_strengths": t.key_strengths,
                "improvement_areas": t.improvement_areas
            } for t in s.turns]

            formatted_sessions.append({
                "id": s.id,
                "session_title": s.session_title,
                "target_company": s.target_company,
                "experience_level": s.experience_level,
                "overall_score": s.overall_score,
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "summary_feedback": s.summary_feedback,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "turns_count": len(s.turns),
                "turns": turns_summary
            })

        formatted_code_runs = [{
            "id": r.id,
            "execution_type": r.execution_type,
            "success": r.success,
            "execution_time_ms": r.execution_time_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in code_runs]

        return UserHistoryResponse(
            user=UserResponse.model_validate(candidate),
            mcq_attempts_count=total_mcqs,
            mcq_accuracy_pct=accuracy_pct,
            interview_sessions_count=total_sessions,
            average_interview_score=avg_score,
            recent_mcq_attempts=[MCQAttemptResponse.model_validate(a) for a in mcq_attempts[:20]],
            recent_interview_sessions=formatted_sessions,
            recent_code_executions=formatted_code_runs
        )

    @staticmethod
    def get_personalized_recommendations(candidate: Candidate, db: Session) -> PersonalizedRecommendationsResponse:
        """Analyzes candidate requirements, key skills, and past performance to provide tailored recommendations."""
        user_skills = candidate.key_skills or ["Python", "SQL", "Docker", "Redis", "Distributed Systems"]
        target_companies = candidate.target_companies or ["Google", "Amazon"]
        
        # Load user attempts
        mcq_attempts = db.query(UserMCQAttempt).filter(UserMCQAttempt.candidate_id == candidate.id).all()
        
        # Map domain performance
        domain_stats: Dict[str, Dict[str, int]] = {}
        for att in mcq_attempts:
            dom = (att.domain or "General").lower()
            if dom not in domain_stats:
                domain_stats[dom] = {"total": 0, "correct": 0}
            domain_stats[dom]["total"] += 1
            if att.is_correct:
                domain_stats[dom]["correct"] += 1

        skills_breakdown: List[SkillAssessment] = []
        weak_areas: List[str] = []
        strengths: List[str] = []

        total_mastery_sum = 0

        for skill in user_skills:
            skill_lower = skill.lower()
            # Match domain or substring
            matched_stats = {"total": 0, "correct": 0}
            for d_name, d_val in domain_stats.items():
                if skill_lower in d_name or d_name in skill_lower:
                    matched_stats["total"] += d_val["total"]
                    matched_stats["correct"] += d_val["correct"]

            tested = matched_stats["total"]
            correct = matched_stats["correct"]

            if tested == 0:
                mastery = 35 # baseline unproven
                status_str = "untested"
                weak_areas.append(f"{skill} (Untested)")
            else:
                pct = int((correct / tested) * 100)
                mastery = pct
                if pct >= 75:
                    status_str = "mastered"
                    strengths.append(f"{skill} ({pct}% Mastery)")
                elif pct >= 50:
                    status_str = "in_progress"
                    weak_areas.append(f"{skill} (Needs Polish, {pct}%)")
                else:
                    status_str = "needs_practice"
                    weak_areas.append(f"{skill} (High Priority Gap, {pct}%)")

            total_mastery_sum += mastery
            skills_breakdown.append(SkillAssessment(
                skill=skill,
                mastery_pct=mastery,
                status=status_str,
                questions_tested=tested,
                correct_count=correct
            ))

        # Overall readiness score based on skill mastery & interview sessions
        avg_mastery = int(total_mastery_sum / len(user_skills)) if user_skills else 50
        interviews_bonus = min(20, (candidate.interviews_completed or 0) * 5)
        overall_readiness = min(100, int((avg_mastery * 0.8) + interviews_bonus))

        # Action Plan tailored to target role and target companies
        primary_company = target_companies[0] if target_companies else "Tier-1 Tech"
        action_plan = [
            f"Target Company Focus: Prioritize {primary_company} high-frequency architectural and core coding benchmarks.",
            f"Skill Gap Remediation: Drill into {weak_areas[0] if weak_areas else user_skills[0]} through interactive MCQ scenarios.",
            f"Bar Raiser Calibration: Complete at least 1 mock interview session on {user_skills[0] if user_skills else 'System Design'} under 15-minute timed pressure.",
            f"Complexity Profiling: Practice big-O runtime invariants and database indexing query plans."
        ]

        # Prioritize matching questions
        all_questions = db.query(InterviewQuestion).all()
        recommended: List[Dict[str, Any]] = []

        # Find questions matching target companies or key skills
        for q in all_questions:
            q_category = (q.category or "").lower()
            q_title = (q.title or "").lower()
            q_companies = [c.lower() for c in (q.company_tags or [])]

            matches_company = any(tc.lower() in q_companies for tc in target_companies)
            matches_skill = any(sk.lower() in q_category or sk.lower() in q_title for sk in user_skills)

            priority_score = 0
            if matches_company:
                priority_score += 50
            if matches_skill:
                priority_score += 40
            priority_score += min(20, (q.frequency_score or 50) // 5)

            if priority_score > 0:
                recommended.append({
                    "id": q.id,
                    "slug": q.slug,
                    "title": q.title,
                    "domain": q.category,
                    "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
                    "ask_frequency": q.frequency_score or 85,
                    "company_tags": q.company_tags or [],
                    "priority_score": priority_score,
                    "invariant_principle": (q.theory_explanation[:150] + "...") if q.theory_explanation else "First-principles engineering invariant"
                })

        # Sort by priority score desc and limit to top 8
        recommended.sort(key=lambda x: x["priority_score"], reverse=True)
        recommended = recommended[:8]

        return PersonalizedRecommendationsResponse(
            candidate_id=candidate.id,
            target_role=candidate.target_role,
            target_companies=target_companies,
            key_skills=user_skills,
            overall_readiness_score=overall_readiness,
            skills_breakdown=skills_breakdown,
            weak_areas=weak_areas,
            strengths=strengths,
            tailored_action_plan=action_plan,
            recommended_questions=recommended
        )
