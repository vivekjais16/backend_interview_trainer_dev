from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_optional_current_user
from app.models.user import Candidate
from app.services.ai_service import ai_service
from app.schemas.llm import LLMAskRequest, LLMAskResponse, LLMPreset

router = APIRouter(prefix="/llm", tags=["LLM Conversational Assistant & Problem Solver"])

PRESET_QUESTIONS = [
    LLMPreset(
        title="Distributed Rate Limiter",
        category="System Design",
        prompt="How do I design a high-throughput distributed rate limiter with sliding window counter in Redis without race conditions?",
        code_sample="""# Python / Redis Sliding Window Counter
import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def is_allowed(user_id: str, limit: int = 100, window_secs: int = 60) -> bool:
    now = time.time()
    key = f"rate_limit:{user_id}"
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_secs)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_secs)
    _, _, req_count, _ = pipe.execute()
    return req_count <= limit
"""
    ),
    LLMPreset(
        title="Python GIL & Subinterpreters",
        category="Python Internals",
        prompt="Explain why the GIL exists in CPython, why CPU-bound threads do not scale across multiple cores, and how PEP 684 per-interpreter GIL solves this.",
        code_sample=None
    ),
    LLMPreset(
        title="B+ Tree Indexing & Range Queries",
        category="SQL & Databases",
        prompt="How does MySQL InnoDB B+ Tree index order rows, and why does a query with LIKE '%search%' cause a full table scan while LIKE 'search%' uses index range scan?",
        code_sample="""-- Comparison of SARGable vs Non-SARGable Query
-- Uses Index Range Scan (B+ Tree prefix match)
SELECT id, email, created_at FROM users WHERE email LIKE 'admin%';

-- Forces Full Table Scan (Cannot seek on leaf node prefix)
SELECT id, email, created_at FROM users WHERE email LIKE '%admin%';
"""
    ),
    LLMPreset(
        title="Raft Consensus & Split-Brain Prevention",
        category="Distributed Systems",
        prompt="How does the Raft consensus algorithm prevent split-brain during a network partition, and why must a quorum be strict majority (N/2 + 1)?",
        code_sample=None
    ),
    LLMPreset(
        title="Cache Stampede & Probabilistic Early Expiration",
        category="Caching & Performance",
        prompt="What is a Cache Stampede (Thundering Herd), and how does the XFetch probabilistic early expiration algorithm prevent database downtime?",
        code_sample="""# XFetch Probabilistic Early Expiration
import math
import random
import time

def should_recompute(ttl_remaining: float, delta_compute_time: float, beta: float = 1.0) -> bool:
    \"\"\"XFetch algorithm (Vattani et al.): recomputes before expiration probabilistically.\"\"\"
    if ttl_remaining <= 0:
        return True
    return -(delta_compute_time * beta * math.log(random.random())) >= ttl_remaining
"""
    )
]

@router.post("/ask", response_model=LLMAskResponse)
async def ask_llm_assistant(
    payload: LLMAskRequest,
    current_user: Optional[Candidate] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Answers any arbitrary user problem question, system design challenge, or code snippet using LLM 
    (Gemini / OpenAI / Ollama / First-Principles Engine) with interactive follow-up chips.
    """
    try:
        # Calibrate target company from payload or candidate profile
        company = payload.target_company
        if current_user and current_user.target_companies and not payload.target_company:
            company = current_user.target_companies[0]

        res = await ai_service.ask_llm(
            question=payload.question,
            code_context=payload.code_context,
            mode=payload.mode,
            target_company=company or "Google",
            conversation_history=payload.conversation_history
        )
        return LLMAskResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query error: {str(e)}")

@router.get("/presets", response_model=List[LLMPreset])
def get_preset_prompts():
    """Returns curated Tier-1 engineering problem prompts for instant testing."""
    return PRESET_QUESTIONS
