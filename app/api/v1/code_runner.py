from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.execution import ExecutionLog
from app.schemas.execution import PythonRunRequest, PythonRunResponse
from app.services.python_runner import run_python_code

router = APIRouter(prefix="/sandbox/python", tags=["Python Sandbox"])

@router.post("", response_model=PythonRunResponse)
def execute_python_sandbox(payload: PythonRunRequest, db: Session = Depends(get_db)):
    timeout = min(payload.timeout_seconds or 5, settings.CODE_EXECUTION_TIMEOUT_SECONDS)
    result = run_python_code(payload.code, timeout_seconds=timeout)

    # Log execution in DB
    try:
        log = ExecutionLog(
            execution_type="python",
            code_content=payload.code,
            stdout=result["stdout"],
            stderr=result["stderr"],
            success=result["success"],
            execution_time_ms=result["execution_time_ms"]
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return result
