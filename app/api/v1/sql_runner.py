from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.config import settings
from app.core.container import get_database_execution_service, get_analytics_service
from app.contracts.execution import DatabaseExecutionContract
from app.contracts.analytics import AnalyticsServiceContract
from app.schemas.execution import SQLRunRequest, SQLRunResponse

router = APIRouter(prefix="/sandbox/sql", tags=["SQL Sandbox"])

@router.post("", response_model=SQLRunResponse)
def execute_sql_sandbox(
    payload: SQLRunRequest,
    db: Session = Depends(get_db),
    sql_svc: DatabaseExecutionContract = Depends(get_database_execution_service),
    analytics_svc: AnalyticsServiceContract = Depends(get_analytics_service)
):
    """Executes SQL query in sandbox and inspects execution plan."""
    result = sql_svc.execute(
        query=payload.query,
        schema_name=payload.schema_name or "ecommerce",
        include_explain=payload.include_explain,
        max_rows=settings.SQL_MAX_ROWS
    )

    # Decoupled telemetry logging
    analytics_svc.log_execution(
        execution_type="sql",
        code_content=payload.query,
        stdout=f"Rows: {result.get('row_count', 0)}",
        stderr=result.get("error"),
        success=result.get("success", False),
        execution_time_ms=result.get("execution_time_ms", 0.0),
        db=db
    )

    return result

@router.get("/schemas")
def get_sql_schemas_metadata(
    sql_svc: DatabaseExecutionContract = Depends(get_database_execution_service)
) -> Dict[str, Any]:
    """Retrieves available SQL sandbox schemas."""
    return {"schemas": sql_svc.get_schemas()}
