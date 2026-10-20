from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.core.container import get_document_execution_service
from app.contracts.execution import DocumentExecutionContract

router = APIRouter(prefix="/sandbox/nosql", tags=["NoSQL / MongoDB Sandbox"])

class NoSQLRunRequest(BaseModel):
    query: str = Field(..., description="MongoDB style find or aggregate query")

class NoSQLRunResponse(BaseModel):
    success: bool
    documents: List[Dict[str, Any]]
    document_count: int
    execution_time_ms: float
    error: Optional[str] = None

@router.post("", response_model=NoSQLRunResponse)
def execute_nosql_sandbox(
    payload: NoSQLRunRequest,
    doc_svc: DocumentExecutionContract = Depends(get_document_execution_service)
):
    """Executes MongoDB query or aggregation pipeline against isolated collections."""
    return doc_svc.execute(payload.query)
