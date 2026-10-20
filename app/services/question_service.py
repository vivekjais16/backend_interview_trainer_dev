from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.contracts.questions import QuestionServiceContract
from app.models.question import InterviewQuestion
from app.schemas.question import QuestionSummary, QuestionDetail, MCQVerifyResponse, MCQQuizItem

class QuestionDomainService(QuestionServiceContract):
    """
    Decoupled Domain Service for Interview Questions and MCQ Speed Arena.
    Encapsulates all database interactions, multi-domain categorizations, and career phase filtering.
    """

    def get_phases(self, db: Session) -> Dict[str, Any]:
        """Calculates and returns career progression phase metrics."""
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

    def list_questions(
        self,
        phase: Optional[str] = None,
        experience_years: Optional[int] = None,
        experience_level: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
        db: Session = None
    ) -> List[QuestionSummary]:
        if not db:
            return []

        query = db.query(InterviewQuestion)

        # 1. Phase filtering
        if phase:
            p_clean = phase.lower()
            if p_clean == "advanced":
                query = query.filter(or_(InterviewQuestion.phase == "advanced", InterviewQuestion.phase == "architect"))
            else:
                query = query.filter(InterviewQuestion.phase == p_clean)

        # 2. Experience level calibration
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

        # 3. Domain Category Groupings
        if category:
            cat_str = str(category).lower().strip()
            if cat_str in ("python_internals", "python"):
                query = query.filter(
                    or_(
                        InterviewQuestion.category == "python_internals",
                        InterviewQuestion.category == "async_concurrency",
                        InterviewQuestion.category == "fastapi_architecture"
                    )
                )
            elif cat_str in ("postgres_mysql", "sql", "sql_database_internals"):
                query = query.filter(
                    or_(
                        InterviewQuestion.category == "postgres_mysql",
                        InterviewQuestion.category == "sql_database_internals"
                    )
                )
            elif cat_str in ("kafka_messaging", "kafka"):
                query = query.filter(
                    or_(
                        InterviewQuestion.category == "kafka_messaging",
                        InterviewQuestion.category == "system_design_mnc"
                    )
                )
            elif cat_str in ("docker_containers", "docker"):
                query = query.filter(InterviewQuestion.category == "docker_containers")
            elif cat_str in ("kubernetes_devops", "k8s"):
                query = query.filter(InterviewQuestion.category == "kubernetes_devops")
            elif cat_str in ("cicd_pipelines", "cicd"):
                query = query.filter(InterviewQuestion.category == "cicd_pipelines")
            elif cat_str in ("mongodb_nosql", "nosql", "mongo"):
                query = query.filter(InterviewQuestion.category == "mongodb_nosql")
            elif cat_str in ("redis_caching", "redis"):
                query = query.filter(InterviewQuestion.category == "redis_caching")
            elif cat_str in ("celery_rabbitmq", "celery"):
                query = query.filter(InterviewQuestion.category == "celery_rabbitmq")
            else:
                query = query.filter(InterviewQuestion.category == cat_str)

        # 4. Difficulty filtering
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty == difficulty)

        # 5. Search query matching
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                or_(
                    InterviewQuestion.title.ilike(search_fmt),
                    InterviewQuestion.scenario_text.ilike(search_fmt)
                )
            )

        questions = query.order_by(InterviewQuestion.frequency_score.desc(), InterviewQuestion.id.asc()).all()

        # 6. Company tag filtering
        if company:
            comp_lower = company.lower()
            questions = [
                q for q in questions 
                if any(comp_lower in str(tag).lower() for tag in (q.company_tags or []))
            ]

        # Convert to QuestionSummary
        results = []
        for q in questions:
            results.append(QuestionSummary(
                id=q.id,
                title=q.title,
                slug=q.slug,
                category=q.category,
                difficulty=q.difficulty,
                min_exp_years=q.min_exp_years,
                max_exp_years=q.max_exp_years,
                company_tags=q.company_tags or [],
                frequency_score=q.frequency_score or 85,
                mindmap_topic=q.mindmap_topic,
                has_python_sandbox=bool(q.has_python_sandbox),
                has_sql_sandbox=bool(q.has_sql_sandbox),
                has_redis_sandbox=bool(q.has_redis_sandbox),
                has_nosql_sandbox=bool(q.has_nosql_sandbox),
                phase=q.phase or "basic",
                has_mcq=bool(q.mcq_question and q.mcq_options and len(q.mcq_options) >= 2)
            ))
        return results

    def get_question(self, question_id_or_slug: Union[int, str], db: Session) -> Optional[InterviewQuestion]:
        if isinstance(question_id_or_slug, int) or (isinstance(question_id_or_slug, str) and question_id_or_slug.isdigit()):
            return db.query(InterviewQuestion).filter(InterviewQuestion.id == int(question_id_or_slug)).first()
        return db.query(InterviewQuestion).filter(InterviewQuestion.slug == str(question_id_or_slug)).first()

    def get_mcq_quiz(self, phase: Optional[str], db: Session) -> List[MCQQuizItem]:
        query = db.query(InterviewQuestion).filter(InterviewQuestion.mcq_question.isnot(None))
        
        if phase:
            p_clean = phase.lower()
            if p_clean == "advanced":
                query = query.filter(or_(InterviewQuestion.phase == "advanced", InterviewQuestion.phase == "architect"))
            else:
                query = query.filter(InterviewQuestion.phase == p_clean)
                
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

    def verify_mcq(self, question_id: int, selected_index: int, db: Session) -> Optional[MCQVerifyResponse]:
        q = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not q or not q.mcq_options:
            return None
            
        is_correct = (selected_index == q.mcq_correct_index)
        explanation = q.mcq_explanation or (q.theory_explanation[:400] if q.theory_explanation else "No explanation available.")
        
        return MCQVerifyResponse(
            is_correct=is_correct,
            correct_index=q.mcq_correct_index,
            explanation=explanation,
            question_id=q.id
        )

# Default singleton instance
question_service = QuestionDomainService()
