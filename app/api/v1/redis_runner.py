from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from app.core.container import get_cache_execution_service
from app.contracts.execution import CacheExecutionContract

router = APIRouter(prefix="/sandbox/redis", tags=["Redis Sandbox"])

class RedisRunRequest(BaseModel):
    commands: str = Field(..., description="Redis commands separated by newlines")

class RedisRunResponse(BaseModel):
    success: bool
    logs: List[Dict[str, Any]]
    execution_time_ms: float

@router.post("", response_model=RedisRunResponse)
def execute_redis_sandbox(
    payload: RedisRunRequest,
    cache_svc: CacheExecutionContract = Depends(get_cache_execution_service)
):
    """Executes Redis CLI commands in an in-memory cache emulator sandbox."""
    return cache_svc.execute(payload.commands)
