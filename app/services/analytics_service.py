from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.contracts.analytics import AnalyticsServiceContract
from app.models.question import InterviewQuestion
from app.models.session import InterviewSession
from app.models.execution import ExecutionLog
from app.core.config import settings
from app.core.database import is_fallback_sqlite

class AnalyticsDomainService(AnalyticsServiceContract):
    """
    Decoupled Domain Service for Telemetry, Execution Logging, and Platform Analytics.
    """

    def get_system_stats(self, db: Session) -> Dict[str, Any]:
        q_count = db.query(InterviewQuestion).count()
        s_count = db.query(InterviewSession).count()
        e_count = db.query(ExecutionLog).count()

        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "database_engine": "SQLite (Local Fallback)" if is_fallback_sqlite else "MySQL (Production)",
            "ai_provider": settings.AI_PROVIDER,
            "stats": {
                "total_questions": q_count,
                "mock_interviews_conducted": s_count,
                "code_executions": e_count
            },
            "experience_tracks": [
                {"level": "junior", "years": "0 - 2 Years", "label": "Junior Software Engineer"},
                {"level": "mid", "years": "3 - 5 Years", "label": "Mid-Level Backend Engineer"},
                {"level": "senior", "years": "6 - 9 Years", "label": "Senior Backend Engineer"},
                {"level": "lead", "years": "10+ Years", "label": "Staff / Principal / Architect"}
            ],
            "ecosystem_domains": [
                {"id": "python_internals", "name": "Python & Asyncio Internals", "icon": "🐍"},
                {"id": "postgres_mysql", "name": "PostgreSQL & MySQL Architecture", "icon": "🐘"},
                {"id": "mongodb_nosql", "name": "MongoDB & Distributed NoSQL", "icon": "🍃"},
                {"id": "redis_caching", "name": "Redis Caching & Distributed Locks", "icon": "⚡"},
                {"id": "kafka_messaging", "name": "Apache Kafka & Event Streaming", "icon": "📨"},
                {"id": "celery_rabbitmq", "name": "Celery & RabbitMQ Task Queues", "icon": "🌿"},
                {"id": "docker_containers", "name": "Docker & Container Hardening", "icon": "🐳"},
                {"id": "kubernetes_devops", "name": "Kubernetes & Cloud-Native Resiliency", "icon": "☸️"},
                {"id": "cicd_pipelines", "name": "CI/CD, SRE & Blue-Green Rollouts", "icon": "🔄"},
                {"id": "system_design_mnc", "name": "MNC High-Scale System Design", "icon": "🏛️"}
            ]
        }

    def log_execution(
        self,
        execution_type: str,
        code_content: str,
        stdout: Optional[str],
        stderr: Optional[str],
        success: bool,
        execution_time_ms: float,
        db: Session
    ) -> None:
        try:
            log = ExecutionLog(
                execution_type=execution_type,
                code_content=code_content,
                stdout=stdout,
                stderr=stderr,
                success=success,
                execution_time_ms=execution_time_ms
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()

# Default singleton instance
analytics_service = AnalyticsDomainService()
