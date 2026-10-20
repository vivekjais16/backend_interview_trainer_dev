from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.services.nosql_runner import run_nosql_query

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
def execute_nosql_sandbox(payload: NoSQLRunRequest):
    result = run_nosql_query(payload.query)
    return result
