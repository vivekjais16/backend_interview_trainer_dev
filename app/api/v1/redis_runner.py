from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from app.services.redis_runner import run_redis_commands

router = APIRouter(prefix="/sandbox/redis", tags=["Redis Sandbox"])

class RedisRunRequest(BaseModel):
    commands: str = Field(..., description="Redis commands separated by newlines")

class RedisRunResponse(BaseModel):
    success: bool
    logs: List[Dict[str, Any]]
    execution_time_ms: float

@router.post("", response_model=RedisRunResponse)
def execute_redis_sandbox(payload: RedisRunRequest):
    result = run_redis_commands(payload.commands)
    return result
