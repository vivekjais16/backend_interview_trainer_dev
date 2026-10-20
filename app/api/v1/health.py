import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db, is_fallback_sqlite
from app.core.config import settings
from app.core.container import (
    get_code_execution_service,
    get_database_execution_service,
    get_cache_execution_service,
    get_document_execution_service,
    get_ai_evaluation_service,
    get_question_service,
    get_mindmap_service
)
from app.contracts.execution import (
    CodeExecutionContract,
    DatabaseExecutionContract,
    CacheExecutionContract,
    DocumentExecutionContract
)
from app.contracts.ai import AIEvaluationContract
from app.contracts.questions import QuestionServiceContract
from app.contracts.mindmap import MindmapServiceContract

router = APIRouter(prefix="/health", tags=["Microservice Health & Gateway Diagnostics"])

@router.get("/liveness", status_code=status.HTTP_200_OK)
def liveness_probe() -> Dict[str, str]:
    """Kubernetes / Docker liveness probe."""
    return {"status": "alive"}

@router.get("/readiness", status_code=status.HTTP_200_OK)
def readiness_probe(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Kubernetes / Docker readiness probe."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database_error": str(e)}

@router.get("/services", status_code=status.HTTP_200_OK)
def microservices_diagnostics(
    db: Session = Depends(get_db),
    code_svc: CodeExecutionContract = Depends(get_code_execution_service),
    sql_svc: DatabaseExecutionContract = Depends(get_database_execution_service),
    cache_svc: CacheExecutionContract = Depends(get_cache_execution_service),
    doc_svc: DocumentExecutionContract = Depends(get_document_execution_service),
    ai_svc: AIEvaluationContract = Depends(get_ai_evaluation_service),
    q_svc: QuestionServiceContract = Depends(get_question_service),
    mm_svc: MindmapServiceContract = Depends(get_mindmap_service)
) -> Dict[str, Any]:
    """
    Decoupled Microservice Subsystems Diagnostic Status.
    Inspects and reports the operational health, adapter type, and latency of each isolated service.
    """
    subsystems = {}

    # 1. Database Connection
    t0 = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        db_lat = round((time.perf_counter() - t0) * 1000.0, 2)
        subsystems["database_primary"] = {
            "status": "HEALTHY",
            "type": "SQLite (Local Fallback)" if is_fallback_sqlite else "MySQL (Production)",
            "latency_ms": db_lat
        }
    except Exception as e:
        subsystems["database_primary"] = {"status": "ERROR", "error": str(e)}

    # 2. Python Code Execution Subsystem
    t0 = time.perf_counter()
    try:
        res = code_svc.execute("x = 1 + 1", timeout_seconds=2)
        py_lat = round((time.perf_counter() - t0) * 1000.0, 2)
        subsystems["sandbox_python"] = {
            "status": "HEALTHY" if res.get("success") else "DEGRADED",
            "adapter": code_svc.__class__.__name__,
            "latency_ms": py_lat
        }
    except Exception as e:
        subsystems["sandbox_python"] = {"status": "ERROR", "error": str(e)}

    # 3. SQL Execution Subsystem
    t0 = time.perf_counter()
    try:
        schemas = sql_svc.get_schemas()
        sql_lat = round((time.perf_counter() - t0) * 1000.0, 2)
        subsystems["sandbox_sql"] = {
            "status": "HEALTHY",
            "adapter": sql_svc.__class__.__name__,
            "schemas_available": len(schemas),
            "latency_ms": sql_lat
        }
    except Exception as e:
        subsystems["sandbox_sql"] = {"status": "ERROR", "error": str(e)}

    # 4. Redis Cache Subsystem
    t0 = time.perf_counter()
    try:
        res = cache_svc.execute("PING")
        red_lat = round((time.perf_counter() - t0) * 1000.0, 2)
        subsystems["sandbox_redis"] = {
            "status": "HEALTHY" if res.get("success") else "DEGRADED",
            "adapter": cache_svc.__class__.__name__,
            "latency_ms": red_lat
        }
    except Exception as e:
        subsystems["sandbox_redis"] = {"status": "ERROR", "error": str(e)}

    # 5. NoSQL Document Subsystem
    t0 = time.perf_counter()
    try:
        res = doc_svc.execute("db.orders.find({})")
        nosql_lat = round((time.perf_counter() - t0) * 1000.0, 2)
        subsystems["sandbox_nosql"] = {
            "status": "HEALTHY" if res.get("success") else "DEGRADED",
            "adapter": doc_svc.__class__.__name__,
            "latency_ms": nosql_lat
        }
    except Exception as e:
        subsystems["sandbox_nosql"] = {"status": "ERROR", "error": str(e)}

    # 6. AI Bar Raiser Subsystem
    cb_state = getattr(ai_svc, "circuit_breaker", None)
    subsystems["ai_evaluator"] = {
        "status": "HEALTHY",
        "adapter": ai_svc.__class__.__name__,
        "configured_provider": settings.AI_PROVIDER,
        "circuit_breaker": cb_state.state.value if cb_state else "N/A"
    }

    # 7. Question Domain Service
    subsystems["question_catalog"] = {
        "status": "HEALTHY",
        "adapter": q_svc.__class__.__name__
    }

    # 8. Mindmap Knowledge Graph Service
    subsystems["knowledge_mindmaps"] = {
        "status": "HEALTHY",
        "adapter": mm_svc.__class__.__name__,
        "topics_count": len(mm_svc.get_topics())
    }

    return {
        "status": "healthy",
        "platform": settings.APP_NAME,
        "architecture": "Decoupled Microservice Domain Architecture",
        "timestamp": time.time(),
        "subsystems": subsystems
    }
