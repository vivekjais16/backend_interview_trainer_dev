import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

MNC_CRITERIA_RUBRIC = """
Evaluate candidate answer on 5 MNC engineering dimensions:
1. Architectural & Theoretical Depth: Does the candidate understand internal mechanisms (GIL, event loop, InnoDB B+ Trees, ACID, memory ref-counts)?
2. Real-Time Production Viability: Will this work under 50,000 req/sec, or will it cause connection pool exhaustion / deadlocks / memory leaks?
3. Code Quality & Idiomatic Style: Clean Pythonic structure, type hinting, exception handling.
4. Edge Case & Failure Resiliency: Circuit breakers, timeouts, race conditions, idempotency.
5. Experience Calibration: Is the answer appropriate for their YOE (Junior: foundational clarity; Senior: trade-offs, P99 latency, cost, distributed consensus)?
"""

class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.AI_MODEL_NAME

    async def evaluate_candidate_turn(
        self,
        question_title: str,
        scenario_text: str,
        experience_level: str,
        target_company: str,
        candidate_response: Optional[str] = None,
        candidate_code: Optional[str] = None,
        candidate_sql: Optional[str] = None,
        previous_cross_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate response and generates deep MNC cross-questions.
        Uses configured provider (Gemini, OpenAI, Ollama) or falls back to the deterministic MNC engine.
        """
        # If API keys are available, call live LLMs
        if self.provider == "gemini" and self.gemini_key:
            try:
                return await self._call_gemini(
                    question_title, scenario_text, experience_level, target_company,
                    candidate_response, candidate_code, candidate_sql, previous_cross_questions
                )
            except Exception as e:
                logger.error(f"Gemini API error, falling back to offline evaluator: {e}")

        elif self.provider == "openai" and self.openai_key:
            try:
                return await self._call_openai(
                    question_title, scenario_text, experience_level, target_company,
                    candidate_response, candidate_code, candidate_sql, previous_cross_questions
                )
            except Exception as e:
                logger.error(f"OpenAI API error, falling back to offline evaluator: {e}")

        elif self.provider == "ollama":
            try:
                return await self._call_ollama(
                    question_title, scenario_text, experience_level, target_company,
                    candidate_response, candidate_code, candidate_sql, previous_cross_questions
                )
            except Exception as e:
                logger.error(f"Ollama error, falling back to offline evaluator: {e}")

        # Deterministic MNC Interviewer Fallback (Zero-cost, works offline)
        return self._evaluate_offline_mnc(
            question_title, scenario_text, experience_level, target_company,
            candidate_response, candidate_code, candidate_sql, previous_cross_questions
        )

    def _evaluate_offline_mnc(
        self,
        question_title: str,
        scenario_text: str,
        experience_level: str,
        target_company: str,
        candidate_response: Optional[str],
        candidate_code: Optional[str],
        candidate_sql: Optional[str],
        previous_cross_questions: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Heuristic-based evaluator simulating a Staff Principal Engineer at Google/Amazon/Uber.
        """
        response_text = (candidate_response or "") + " " + (candidate_code or "") + " " + (candidate_sql or "")
        lower = response_text.lower()
        word_count = len(response_text.split())

        base_score = 6.0
        strengths = []
        improvements = []
        cross_questions = []

        # Keywords checking
        has_concurrency = any(w in lower for w in ["async", "await", "thread", "process", "lock", "race condition", "event loop"])
        has_db_depth = any(w in lower for w in ["index", "b-tree", "b+ tree", "acid", "isolation", "transaction", "innodb", "explain", "n+1"])
        has_performance = any(w in lower for w in ["p99", "latency", "throughput", "cache", "redis", "pool", "batch", "memory"])
        has_tradeoffs = any(w in lower for w in ["trade-off", "bottleneck", "alternatively", "drawback", "at scale", "benchmark"])
        has_idempotency = any(w in lower for w in ["idempotent", "retry", "kafka", "queue", "dead letter", "circuit breaker"])

        if word_count > 60:
            base_score += 1.0
            strengths.append("Provided a structured and articulate explanation.")
        else:
            base_score -= 1.0
            improvements.append("Response is brief. Top MNC interviewers expect deep exploration of system boundaries and failure states.")

        if has_concurrency:
            base_score += 0.8
            strengths.append("Demonstrated solid awareness of concurrency and non-blocking I/O execution.")
        else:
            improvements.append("Didn't explicitly highlight concurrency behavior (e.g., event loop starvation or race conditions).")

        if has_db_depth:
            base_score += 0.8
            strengths.append("Addressed database indexing, transaction guarantees, or query plan execution.")
        
        if has_tradeoffs:
            base_score += 0.7
            strengths.append("Highlighted critical engineering trade-offs rather than proposing a naive silver bullet.")
        else:
            improvements.append("Consider discussing edge cases and failure modes (e.g. timeout, partial failure, network partitions).")

        # Adjust score according to experience level expectations
        if experience_level == "junior":
            final_score = min(9.5, max(4.0, base_score + 1.0))
            cross_questions = [
                f"How would you write a unit test to verify this logic handles invalid or null inputs?",
                f"If this function is called 10,000 times in a loop, what is the Big-O time and space complexity?"
            ]
        elif experience_level == "mid":
            final_score = min(9.0, max(3.5, base_score))
            cross_questions = [
                f"In FastAPI, what happens if this logic executes a blocking synchronous I/O call inside an `async def` route? How would you prevent event-loop starvation?",
                f"How would you ensure database connection pool sizing (`pool_size`, `max_overflow`) doesn't get overwhelmed under peak traffic surges?"
            ]
        elif experience_level == "senior":
            final_score = min(8.8, max(3.0, base_score - 0.5))
            cross_questions = [
                f"Suppose two concurrent requests attempt to modify the same resource simultaneously. How do you prevent lost updates: Optimistic locking with version tags or Pessimistic `SELECT FOR UPDATE`? What are the deadlock risks?",
                f"If the downstream payment/service responds with an HTTP 504 Gateway Timeout, how do you handle retries without causing duplicate charge anomalies?"
            ]
        else: # Lead / Architect
            final_score = min(8.5, max(3.0, base_score - 1.0))
            cross_questions = [
                f"How would you design the distributed state machine for this across multi-region active-active database clusters with minimal replication lag?",
                f"Walk me through your observability strategy: What metrics would trigger PagerDuty alerts for P99 latency degradation?"
            ]

        feedback_md = f"""### 🎯 MNC Interviewer Feedback ({target_company} Bar Raiser Review)

**Overall Rating**: **{final_score:.1f} / 10.0** — *{"Strong Hire" if final_score >= 8.0 else "Hire with Feedback" if final_score >= 6.5 else "Needs Improvement on Deep Internals"}*

#### ✅ Strengths Observed:
{"".join(f"- {s}\\n" for s in (strengths or ["Addressed the primary problem statement directly."]))}

#### ⚠️ Areas for MNC Technical Elevation:
{"".join(f"- {i}\\n" for i in (improvements or ["Elaborate on production observability and distributed recovery patterns."]))}

#### 💡 Staff Engineer Best Practice:
At companies like {target_company}, high-scale backend services prioritize **fault domains**, **predictable P99 latency**, and **zero-data-loss idempotency**. When discussing APIs, always address connection recycling, statement timeouts, and graceful shutdown handling.
"""
        return {
            "score": round(final_score, 1),
            "feedback": feedback_md,
            "cross_questions": cross_questions,
            "key_strengths": strengths,
            "improvement_areas": improvements
        }

    async def _call_gemini(self, question, scenario, exp_level, company, resp, code, sql, prev_q) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
        prompt = f"""
You are an uncompromising Bar Raiser & Staff Backend Engineer conducting a technical interview at {company}.
The candidate has {exp_level} years of experience.
Problem Scenario: {scenario}
Candidate Answer: {resp}
Candidate Python Code: {code}
Candidate SQL Query: {sql}
Previous Cross Questions: {prev_q}

Evaluate the candidate based on:
1. Correctness & edge-case safety.
2. Understanding of Python/FastAPI/MySQL internals (GIL, asyncio loop, B+ Tree indexes, MVCC, connection pools).
3. Production resiliency at high scale.

Return ONLY a JSON object with this exact structure:
{{
  "score": 7.5,
  "feedback": "markdown string with detailed review, strengths, weaknesses and MNC standard",
  "cross_questions": ["probing cross-question 1", "probing cross-question 2"],
  "key_strengths": ["strength 1", "strength 2"],
  "improvement_areas": ["improvement 1", "improvement 2"]
}}
"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
            })
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)

    async def _call_openai(self, question, scenario, exp_level, company, resp, code, sql, prev_q) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        prompt = f"""
You are a Staff Principal Engineer at {company} conducting a backend interview.
Candidate Experience Level: {exp_level}
Scenario: {scenario}
Candidate Response: {resp}
Python Code: {code}
SQL: {sql}

Respond in JSON with keys: score (float 0-10), feedback (markdown), cross_questions (list of 2 strings), key_strengths (list), improvement_areas (list).
"""
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            })
            data = res.json()
            return json.loads(data["choices"][0]["message"]["content"])

    async def _call_ollama(self, question, scenario, exp_level, company, resp, code, sql, prev_q) -> Dict[str, Any]:
        url = f"{self.ollama_url}/api/generate"
        prompt = f"""
You are an MNC Staff Engineer conducting an interview. Return JSON with keys: score, feedback, cross_questions, key_strengths, improvement_areas.
Candidate: {resp} | Code: {code} | SQL: {sql} | Scenario: {scenario}
"""
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(url, json={
                "model": "llama3",
                "prompt": prompt,
                "format": "json",
                "stream": False
            })
            return json.loads(res.json()["response"])

ai_service = AIService()
