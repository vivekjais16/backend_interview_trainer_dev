from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.container import get_code_execution_service, get_analytics_service
from app.contracts.execution import CodeExecutionContract
from app.contracts.analytics import AnalyticsServiceContract
from app.schemas.execution import PythonRunRequest, PythonRunResponse

router = APIRouter(prefix="/sandbox/python", tags=["Python Sandbox"])

@router.post("", response_model=PythonRunResponse)
def execute_python_sandbox(
    payload: PythonRunRequest,
    db: Session = Depends(get_db),
    code_svc: CodeExecutionContract = Depends(get_code_execution_service),
    analytics_svc: AnalyticsServiceContract = Depends(get_analytics_service)
):
    """Executes Python code in a safe sandbox with AST Big-O complexity analysis."""
    timeout = min(payload.timeout_seconds or 5, settings.CODE_EXECUTION_TIMEOUT_SECONDS)
    result = code_svc.execute(payload.code, timeout_seconds=timeout)

    # Decoupled telemetry logging
    analytics_svc.log_execution(
        execution_type="python",
        code_content=payload.code,
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        success=result.get("success", False),
        execution_time_ms=result.get("execution_time_ms", 0.0),
        db=db
    )

    return result
