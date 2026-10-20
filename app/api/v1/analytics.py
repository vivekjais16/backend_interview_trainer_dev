from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db, is_fallback_sqlite
from app.core.config import settings
from app.models.question import InterviewQuestion
from app.models.session import InterviewSession
from app.models.execution import ExecutionLog

router = APIRouter(prefix="/analytics", tags=["Analytics & Health"])

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
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
        ]
    }
