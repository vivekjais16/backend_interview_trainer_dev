from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.container import get_analytics_service
from app.contracts.analytics import AnalyticsServiceContract

router = APIRouter(prefix="/analytics", tags=["Analytics & Health"])

@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db),
    analytics_svc: AnalyticsServiceContract = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """Retrieves system operational metrics, question catalog size, and interview stats."""
    return analytics_svc.get_system_stats(db=db)
