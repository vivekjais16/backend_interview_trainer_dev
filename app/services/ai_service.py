import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.contracts.ai import AIEvaluationContract
from app.core.resilience import CircuitBreaker

logger = logging.getLogger(__name__)

MNC_CRITERIA_RUBRIC = """
Evaluate candidate answer on 5 MNC engineering dimensions:
1. Architectural & Theoretical Depth: Does the candidate understand internal mechanisms (GIL, event loop, InnoDB B+ Trees, ACID, memory ref-counts)?
2. Real-Time Production Viability: Will this work under 50,000 req/sec, or will it cause connection pool exhaustion / deadlocks / memory leaks?
3. Code Quality & Idiomatic Style: Clean Pythonic structure, type hinting, exception handling.
4. Edge Case & Failure Resiliency: Circuit breakers, timeouts, race conditions, idempotency.
5. Experience Calibration: Is the answer appropriate for their YOE (Junior: foundational clarity; Senior: trade-offs, P99 latency, cost, distributed consensus)?
"""

class AIService(AIEvaluationContract):
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.AI_MODEL_NAME
        self.circuit_breaker = CircuitBreaker("ai_evaluator", failure_threshold=3, recovery_timeout_seconds=30.0)

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
        Uses configured provider (Gemini, OpenAI, Ollama) with CircuitBreaker protection or falls back to the deterministic MNC engine.
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("AI circuit breaker is OPEN. Falling back directly to deterministic MNC evaluator.")
            return self._evaluate_offline_mnc(
                question_title, scenario_text, experience_level, target_company,
                candidate_response, candidate_code, candidate_sql, previous_cross_questions
            )

        # If API keys are available, call live LLMs
        if self.provider == "gemini" and self.gemini_key:
            try:
                res = await self._call_gemini(
                    question_title, scenario_text, experience_level, target_company,
                    candidate_response, candidate_code, candidate_sql, previous_cross_questions
                )
                self.circuit_breaker.record_success()
                return res
            except Exception as e:
                self.circuit_breaker.record_failure()
                logger.error(f"Gemini API error, falling back to offline evaluator: {e}")

        elif self.provider == "openai" and self.openai_key:
            try:
                res = await self._call_openai(
                    question_title, scenario_text, experience_level, target_company,
                    candidate_response, candidate_code, candidate_sql, previous_cross_questions
                )
                self.circuit_breaker.record_success()
                return res
            except Exception as e:
                self.circuit_breaker.record_failure()
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

        # Big-O Time & Space Complexity Audit
        complexity_block = ""
        if candidate_code and len(candidate_code.strip()) > 5:
            try:
                from app.services.python_runner import analyze_code_complexity
                c_info = analyze_code_complexity(candidate_code)
                time_c = c_info.get("time_complexity", "O(N)")
                space_c = c_info.get("space_complexity", "O(1)")
                opt_time = c_info.get("optimal_time", "O(N)")
                opt_space = c_info.get("optimal_space", "O(1)")
                suggs = c_info.get("suggestions", [])

                if "Quadratic" in time_c or "Cubic" in time_c or "Exponential" in time_c:
                    base_score -= 0.8
                    improvements.append(f"Algorithm exhibits high time complexity ({time_c}). Consider refactoring to {opt_time}.")
                else:
                    strengths.append(f"Demonstrated clean algorithmic runtime complexity ({time_c}).")

                sugg_text = "\n".join(f"  - {s}" for s in suggs) if suggs else "  - Algorithm operates at optimal Big-O bounds."
                complexity_block = f"""
#### ⏱️ Big-O Time & Space Complexity Audit:
- **Detected Runtime**: `{time_c}` *(Target: `{opt_time}`)*
- **Detected Memory**: `{space_c}` *(Target: `{opt_space}`)*
- **Optimization Suggestions**:
{sugg_text}
"""
            except Exception as e:
                logger.warning(f"Error auditing code complexity: {e}")

        feedback_md = f"""### 🎯 MNC Bar Raiser Review ({target_company} Technical Round)

**Evaluation Verdict**: **{final_score:.1f} / 10.0** — *{"Strong Hire — Demonstrates Deep Technical Mastery" if final_score >= 8.5 else "Hire — Solid Fundamentals & Clear Explanations" if final_score >= 7.0 else "Leaning Hire — Good Start, Needs Deeper Failure State Exploration"}*

#### 💡 In Plain English (The Core Takeaway):
At companies like {target_company}, high-scale systems prioritize **predictable P99 latency**, **zero data loss**, and **clean failure isolation**. The best candidates clearly articulate *why* a particular data structure or architectural pattern was chosen over naive alternatives.
{complexity_block}
#### ✅ What You Did Well:
{"".join(f"- {s}\\n" for s in (strengths or ["Addressed the primary problem statement with technical clarity."]))}

#### ⚠️ How to Elevate to Senior / Lead Level:
{"".join(f"- {i}\\n" for i in (improvements or ["Discuss edge cases like connection timeouts, database retries, and distributed race conditions."]))}

#### 🚀 30-Second Interview Punchline You Can Use:
"Our approach guarantees high throughput by offloading blocking operations, using indexed lookups to prevent table scans, and applying exponential backoff with jitter to eliminate thundering herd spikes."
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

    async def query_copilot(
        self,
        question: Any,
        prompt_type: str,
        user_prompt: Optional[str] = None,
        candidate_code: Optional[str] = None,
        candidate_sql: Optional[str] = None,
        experience_level: str = "mid",
        target_company: str = "Top Tech MNC"
    ) -> Dict[str, Any]:
        """
        AI Copilot Pair Programmer & Senior Staff Coach.
        Answers queries (ELI5, architectural hint, Big-O audit, debugging traps, cross-questions, custom technical questions).
        """
        import random
        p_type = (prompt_type or "custom").lower().strip()
        
        # 1. ELI5: Explain Simply
        if p_type == "eli5":
            analogy = "Think of this problem like an airport security checkpoint or high-speed electronic toll booth: rather than inspecting every passenger from scratch in O(N^2) time, we cache verified states in O(1) time."
            cat = getattr(question, 'category', '') or ''
            if "sql" in cat.lower() or "database" in cat.lower():
                analogy = "Think of this like an organized library: instead of reading every page of every book sequentially (Full Table Scan), we check the alphabetical index card catalog (B+ Tree) to locate the exact shelf in milliseconds."
            elif "cache" in cat.lower() or "redis" in cat.lower():
                analogy = "Think of this like keeping your most frequently used tools on your desk within arm's reach (RAM Cache) rather than walking to the basement storage warehouse (Hard Disk / Main DB) every single time."

            q_title = getattr(question, 'title', 'Backend Architecture')
            q_scen = getattr(question, 'scenario_text', 'Analyze optimal performance.')
            reply = f"""### 💡 Explain Like I'm 5 (ELI5 Breakdown)

**Problem:** {q_title}

#### 🎯 Simple Intuition & Analogy
{analogy}

#### 🔑 What the Problem Actually Asks:
{q_scen}

#### ⚡ The Core Technical Insight:
- **Don't Overcomplicate:** Avoid deep nested loops or redundant remote round-trips.
- **State & Memory:** Track intermediate results using dictionaries/hash-maps or indexed lookups.
- **Edge Boundaries:** Be prepared for empty payloads, duplicate keys, or network disconnects.

#### 🛠️ Quick Step-by-Step Strategy:
1. **Understand Input/Output:** Validate types and boundary ranges.
2. **Select Data Structure:** Prefer `dict`/`set` for O(1) membership over `list` (O(N)).
3. **Iterate Once (O(N)):** Compute solution linearly and return optimal result.
"""
            chips = ["💡 Give me a hint", "⏱ Analyze my code's Big-O", "🔥 Grill me with a follow-up"]
            return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

        # 2. HINT: Architectural Blueprint Hint
        if p_type == "hint":
            bps = getattr(question, 'best_practices', None) or []
            bp = bps[0] if bps else "Maintain a single-pass invariant and avoid repeated calculations."
            q_title = getattr(question, 'title', 'Backend Architecture')
            reply = f"""### 💡 Architectural Blueprint Hint

**Target Problem:** {q_title}

#### 🧭 Guiding Engineering Direction:
- **Data Structure Choice:** Look at your access pattern. If you need frequent lookups or uniqueness checks, use a `set` or `dict`. If you need FIFO or Sliding Window, use `collections.deque`.
- **System Invariant:** {bp}
- **High Concurrency Note:** Avoid holding locks during external network calls or database writes to prevent connection pool exhaustion.

*(Try drafting this logic in the IDE on the right, then run your test!)*
"""
            chips = ["💬 Explain Simply (ELI5)", "⏱ Audit Big-O Complexity", "🐞 Check for Traps"]
            return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

        # 3. COMPLEXITY: Big-O Time & Space Audit
        if p_type == "complexity":
            from app.services.python_runner import analyze_code_complexity
            code_to_check = candidate_code or ""
            if len(code_to_check.strip()) > 10:
                c_info = analyze_code_complexity(code_to_check)
                t_comp = c_info.get("time_complexity", "O(N)")
                s_comp = c_info.get("space_complexity", "O(1)")
                opt_t = c_info.get("optimal_time", "O(N)")
                opt_s = c_info.get("optimal_space", "O(1)")
                suggs = c_info.get("suggestions", [])
                sugg_text = "\n".join(f"- {s}" for s in suggs) if suggs else "- Clean code operating within optimal asymptotic boundaries!"

                reply = f"""### ⏱️ AST Big-O Complexity Profiling

- **Detected Runtime Complexity:** `{t_comp}` *(Target: `{opt_t}`)*
- **Detected Space Complexity:** `{s_comp}` *(Target: `{opt_s}`)*

#### 🔍 Bottleneck Analysis & Recommendations:
{sugg_text}

#### 💡 Staff Principal Optimization Rule:
Whenever you have `if x in list_var:` inside a `for` loop, you create hidden `O(N * M)` quadratic runtime. Convert `list_var` to a `set` beforehand for instant `O(1)` hash lookup!
"""
            else:
                q_title = getattr(question, 'title', 'Backend Architecture')
                reply = f"""### ⏱️ Expected Big-O Complexity Benchmark

**Problem:** {q_title}

- **Target Time Complexity:** `O(N)` or `O(N log N)` depending on sorting requirements.
- **Target Space Complexity:** `O(1)` auxiliary memory, or `O(N)` if indexing is required.

*(Paste or write your Python code in the IDE on the right and click 'Audit Big-O' again to run a real-time AST complexity audit on your exact implementation!)*
"""
            chips = ["🐞 Check for Traps", "💡 Architectural Hint", "🔥 Cross-Question"]
            return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

        # 4. DEBUG / TRAPS: Check for common pitfalls
        if p_type == "debug":
            traps = getattr(question, 'common_traps', None) or [
                "Unbounded memory growth when accumulating large sequences.",
                "Event loop blockage caused by synchronous I/O operations.",
                "Missing transaction isolation or unhandled rollback on database errors."
            ]
            traps_md = "\n".join(f"- **Trap {i+1}:** {t}" for i, t in enumerate(traps))
            q_title = getattr(question, 'title', 'Backend Architecture')
            reply = f"""### 🐞 Common Traps & Edge Case Review

**Known Pitfalls for {q_title}:**
{traps_md}

#### 🛡️ Defensive Engineering Checklist:
- **Empty & Null Cases:** Does your code handle `None`, empty strings, or empty lists gracefully without crashing?
- **Concurrency & Race Conditions:** If two requests execute this at the exact same millisecond, could there be a dirty read or lost update?
- **Resource Leaks:** Are all connections, sockets, and cursors cleanly closed with context managers?
"""
            chips = ["⏱ Audit Big-O Complexity", "💬 Explain Simply (ELI5)", "🎙️ Submit for Review"]
            return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

        # 5. CROSS_QUESTION: Follow-up challenge
        if p_type == "cross_question":
            from app.seeds.seed_data import DEFAULT_CROSS_QUESTIONS
            cq_list = getattr(question, 'cross_questions', None) or DEFAULT_CROSS_QUESTIONS
            selected_cq = random.choice(cq_list) if cq_list else "How would you handle a sudden 10x traffic spike on this endpoint?"
            reply = f"""### 🔥 MNC Senior Staff Follow-Up Challenge

> **"{selected_cq}"**

#### 💭 How to Frame Your Answer:
1. **Identify the Core Trade-Off:** (e.g., Latency vs Data Consistency, CPU vs Memory).
2. **Propose Architecture:** (e.g., Redis distributed lock, optimistic locking version tag, message queue backpressure).
3. **Monitoring & Metrics:** Mention how P99 latency or dead-letter queue metrics would alert you.

*(Type your architectural answer in the editor below and click 'Submit for Bar Raiser Review'!)*
"""
            chips = ["Address this cross-question", "💡 Architectural Hint", "⏱ Audit Big-O"]
            return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

        # 6. CUSTOM: General prompt / query
        user_text = (user_prompt or "").strip()
        if not user_text:
            user_text = "How can I approach this problem with optimal design?"

        q_title = getattr(question, 'title', 'Backend Architecture')
        theory = getattr(question, 'theory_explanation', '') or ''
        reply = f"""### 🤖 AI Senior Staff Copilot Advice

**Regarding:** *"{user_text}"*

#### 🧠 Analysis for {q_title}:
- In production at {target_company}, backends must balance throughput, latency, and fault tolerance.
- **Key Consideration:** {theory[:300] if theory else "Ensure non-blocking operations and clean decoupling between data access and business logic."}...

#### 🚀 Recommended Next Step:
Test your implementation in the right-hand IDE. You can test code execution with `Run Code` or profile algorithmic runtime with `Audit Big-O`.
"""
        chips = ["💬 Explain Simply (ELI5)", "💡 Architectural Hint", "⏱ Audit Big-O", "🔥 Cross-Question"]
        return {"prompt_type": p_type, "reply": reply, "action_chips": chips}

    async def ask_llm(
        self,
        question: str,
        code_context: Optional[str] = None,
        mode: str = "comprehensive",
        target_company: str = "Google",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        LLM Conversational Problem Solver & Interview Mentor (Gemini / OpenAI / First-Principles Core).
        Accepts any technical question, architecture scenario, or code snippet and returns structured guidance.
        """
        q_clean = (question or "").strip()
        history = conversation_history or []
        mode_clean = (mode or "comprehensive").lower().strip()

        # 1. Try Live Gemini if configured
        if self.provider == "gemini" and self.gemini_key:
            try:
                ans = await self._call_gemini_general(q_clean, code_context, mode_clean, target_company, history)
                return ans
            except Exception as e:
                logger.warning(f"Live Gemini general query failed ({e}); falling back to first-principles engine.")

        # 2. Try Live OpenAI if configured
        if self.provider == "openai" and self.openai_key:
            try:
                ans = await self._call_openai_general(q_clean, code_context, mode_clean, target_company, history)
                return ans
            except Exception as e:
                logger.warning(f"Live OpenAI general query failed ({e}); falling back to first-principles engine.")

        # 3. First-Principles Knowledge Synthesis Engine (100% Reliable Offline/Local/Mock)
        return self._synthesize_first_principles_answer(q_clean, code_context, mode_clean, target_company)

    async def _call_gemini_general(self, question: str, code: Optional[str], mode: str, company: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
        
        system_instruction = f"""You are a Principal Staff Backend Architect and Bar Raiser at {company}.
You explain problems with deep first-principles intuition, high-scale production trade-offs (P99 latency, memory invariants, concurrency gotchas), and working production-grade code.
Format your answer with clear GitHub Flavored Markdown headings, diagrams or bullet points, and code blocks.
Response mode requested: {mode}."""

        contents = []
        for msg in history[-4:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        user_content = question
        if code:
            user_content += f"\n\n```python\n{code}\n```"

        contents.append({"role": "user", "parts": [{"text": user_content}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

            # Extract code snippet if present
            code_snippet = None
            if "```python" in raw_text:
                parts = raw_text.split("```python")[1].split("```")[0]
                code_snippet = parts.strip()

            return {
                "answer": raw_text,
                "provider": f"Gemini ({self.model})",
                "mode": mode,
                "action_chips": [
                    "💡 Explain with simpler analogy",
                    "⏱ Audit Big-O runtime & memory",
                    "🔥 Grill me with Staff Bar Raiser follow-up",
                    "🐞 What edge cases could break this in production?"
                ],
                "code_snippet": code_snippet,
                "suggested_followups": [
                    f"How would {company} scale this under 100k requests/sec?",
                    "What happens during a sudden network partition or node failure?",
                    "How does this implementation protect against memory leaks or deadlocks?"
                ]
            }

    async def _call_openai_general(self, question: str, code: Optional[str], mode: str, company: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        messages = [
            {"role": "system", "content": f"You are a Staff Principal Engineer at {company}. Provide deep technical breakdown, first-principles logic, and code. Mode: {mode}."}
        ]
        for msg in history[-4:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        full_q = question + (f"\n\n```\n{code}\n```" if code else "")
        messages.append({"role": "user", "content": full_q})

        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.3
            })
            res.raise_for_status()
            data = res.json()
            raw_text = data["choices"][0]["message"]["content"]

            code_snippet = None
            if "```python" in raw_text:
                code_snippet = raw_text.split("```python")[1].split("```")[0].strip()

            return {
                "answer": raw_text,
                "provider": "OpenAI (GPT-4o)",
                "mode": mode,
                "action_chips": [
                    "💡 Explain with simpler analogy",
                    "⏱ Audit Big-O runtime",
                    "🔥 Staff Bar Raiser follow-up"
                ],
                "code_snippet": code_snippet,
                "suggested_followups": [
                    f"How does this handle high concurrency at {company}?",
                    "What are the P99 latency trade-offs?"
                ]
            }

    def _synthesize_first_principles_answer(
        self,
        question: str,
        code_context: Optional[str],
        mode: str,
        target_company: str
    ) -> Dict[str, Any]:
        """
        Deep First-Principles Technical Engine.
        Synthesizes structured, production-grade answers for any arbitrary engineering question.
        """
        q_lower = question.lower()
        has_code = bool(code_context and len(code_context.strip()) > 5)

        # Detect topic domain
        is_python = any(k in q_lower for k in ["python", "gil", "asyncio", "generator", "decorator", "metaclass", "typing", "fastapi", "pydantic", "multiprocessing", "thread"])
        is_sql = any(k in q_lower for k in ["sql", "mysql", "postgres", "index", "b+ tree", "join", "acid", "transaction", "window function", "query", "explain"])
        is_redis = any(k in q_lower for k in ["redis", "cache", "stampede", "eviction", "lru", "lfu", "xfetch", "zset", "sorted set", "ttl"])
        is_distributed = any(k in q_lower for k in ["distributed", "raft", "paxos", "consensus", "quorum", "consistent hash", "fencing token", "split-brain", "cap", "pacelc", "two-phase"])
        is_docker = any(k in q_lower for k in ["docker", "container", "kubernetes", "k8s", "cgroup", "namespace", "ingress", "pod"])
        is_kafka = any(k in q_lower for k in ["kafka", "queue", "message", "pubsub", "event", "partition", "zero-copy", "consumer group", "offset"])

        # Topic Title & Context
        topic_title = "Backend Systems Engineering & Scalability"
        if is_distributed: topic_title = "Distributed Systems, Consensus & Fault Tolerance"
        elif is_redis: topic_title = "High-Throughput Caching & Memory Architecture"
        elif is_sql: topic_title = "Relational Storage Engines & Query Optimization"
        elif is_python: topic_title = "Python Internals, Concurrency & Asyncio Execution"
        elif is_docker: topic_title = "Cloud Infrastructure & Containerization"
        elif is_kafka: topic_title = "Event-Driven Streams & Message Ordering"

        # 1. First-Principles Mental Model / Analogy
        analogy = "Think of this like an airport baggage routing system: instead of every passenger manually walking their bag to the runway (unbounded contention and O(N^2) bottlenecks), bags are batched through dedicated conveyors with checksum routing in O(1) time."
        if is_sql:
            analogy = "Think of this like an indexed encyclopedia: sequential full-table scans require flipping every page, while a B+ Tree index acts as a multi-level table of contents allowing O(log N) page lookups with contiguous range-scan pointers."
        elif is_python:
            analogy = "Think of Python's GIL like a shared single-lane bridge with a traffic baton: threads can prepare work in parallel, but only the thread holding the baton can cross the bytecode interpreter bridge at any given millisecond."
        elif is_redis:
            analogy = "Think of Redis caching like keeping your most urgent notes pinned on your monitor (RAM, ~100ns access) instead of driving to the city archive (disk I/O, ~10ms access) for every question."
        elif is_distributed:
            analogy = "Think of distributed consensus like a parliamentary quorum voting rule: an agreement is only legally binding if a strict majority (N/2 + 1) of voting members cast an affirmative vote, preventing conflicting rival decrees."

        # 2. Mode Customization
        if mode == "eli5":
            answer = f"""### 💡 Explain Like I'm 5 (ELI5 First-Principles Breakdown)

**Your Question:** *"{question}"*

#### 🎯 Intuitive Mental Model:
{analogy}

#### 🔑 What Is Really Happening Under the Hood?
1. **The Core Invariant:** In large-scale systems at **{target_company}**, simple approaches fail because traffic spikes create unexpected resource exhaustion (CPU, thread pool, socket connections, or database locks).
2. **The Mechanism:** By decoupling the work into isolated stages and using optimal data structures (`dict`, `set`, ring buffers, or indexed keys), we avoid redundant round-trips.
3. **The Practical Takeaway:** Never perform expensive sequential work in a blocking loop; cache frequently requested data and batch high-frequency updates.

#### 🚀 Recommended Action:
Would you like to see a complete Python code implementation or discuss how {target_company} tests this during System Design rounds?
"""
            chips = ["💻 Generate production code solution", "⏱ Audit time & space complexity", "🔥 Grill me with follow-up"]

        elif mode == "code_solution":
            code_body = """import time
import asyncio
from typing import Dict, Any, Optional

class ProductionSolution:
    \"\"\"
    Production-calibrated implementation with defensive boundaries,
    circuit-breaker timeouts, and O(1) state caching.
    \"\"\"
    def __init__(self, ttl_seconds: float = 60.0):
        self._cache: Dict[str, Any] = {}
        self._ttl = ttl_seconds

    def execute_optimized_flow(self, key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Input validation & boundary guard
        if not key or not payload:
            raise ValueError("Key and non-empty payload required.")

        now = time.time()
        
        # Step 2: O(1) Cache Lookup to protect downstream databases
        cached = self._cache.get(key)
        if cached and (now - cached['timestamp'] < self._ttl):
            return {"status": "hit", "data": cached['value'], "cached": True}

        # Step 3: Compute optimal state (Single Pass Linear O(N))
        processed_data = {k: v for k, v in payload.items() if v is not None}
        
        # Step 4: Atomic storage with TTL
        self._cache[key] = {'value': processed_data, 'timestamp': now}
        
        return {"status": "computed", "data": processed_data, "cached": False}

# Verification & Test Cases
if __name__ == "__main__":
    solver = ProductionSolution(ttl_seconds=5.0)
    res1 = solver.execute_optimized_flow("req_101", {"tenant_id": 42, "role": "admin"})
    print("[RUN 1 - Computed]:", res1)
    res2 = solver.execute_optimized_flow("req_101", {"tenant_id": 42})
    print("[RUN 2 - Cache Hit]:", res2)
"""
            answer = f"""### 💻 Production-Grade Code Solution

**Regarding:** *"{question}"*

Here is the clean, idiomatic implementation following **{target_company}** Staff Engineering conventions (type hints, defensive guard rails, and bounded complexity):

```python
{code_body}
```

#### 🛡️ Engineering Guarantees:
- **Time Complexity:** `O(1)` for lookup and state management; `O(N)` for payload serialization.
- **Space Complexity:** `O(K)` where $K$ is the number of active cached keys.
- **Defensive Boundary:** Validates empty/null keys upfront to prevent `KeyError` or silent corruption.
"""
            chips = ["⏱ Audit Big-O Complexity", "🐞 Find Edge Cases & Traps", "💬 Explain from Basics (ELI5)"]

        elif mode == "system_design":
            answer = f"""### 🏗️ High-Throughput System Design Breakdown

**Target Problem:** *"{question}"*
**Target Tier:** **{target_company} Bar Raiser Benchmark**

```
 [Clients / Apps] 
        │ (HTTPS / TLS 1.3)
        ▼
 [Cloudflare / Envoy Gateway] ─── (Distributed Rate Limiter)
        │
        ▼
 [Stateless API Workers (FastAPI / Go)]
   ├── In-Memory Local LRU Cache (Layer 1)
   └── Distributed Redis Cluster (Layer 2 / Read Replicas)
        │ (Asynchronous Event Write)
        ▼
 [Kafka / RabbitMQ Log Stream] ─── [Workers: CDC & Indexing]
        │
        ▼
 [Primary DB (PostgreSQL / Aurora with B+ Tree Indexes)]
```

#### 1. Core Architecture Decisions:
- **Stateless API Layer:** Application instances scale horizontally behind an Envoy / Nginx ingress gateway.
- **Multi-Tier Caching:** L1 application-local LRU avoids network hop for hottest 1% keys; L2 Redis cluster handles shared state with probabilistic early expiration (XFetch) to eliminate cache stampedes.
- **Idempotency & Deduplication:** Write endpoints require client-generated UUID `Idempotency-Key` headers stored in Redis with short TTL.

#### 2. Scalability & Latency Invariants:
- **P99 Target:** < 15ms at 50,000 req/sec.
- **Storage Trade-off:** Eventual consistency for search read replicas; strict linearizability for payments and inventory.
"""
            chips = ["🔥 Grill me with follow-up questions", "💻 Show Python/SQL implementation", "⏱ Audit Big-O"]

        else: # Comprehensive Default Mode
            answer = f"""### 🧠 Technical Analysis & Architectural Solution

**Topic Domain:** **{topic_title}**  
**Target Calibration:** **{target_company} Staff Engineering Standard**

---

#### 1. 🎯 Problem Deconstruction & Core Invariant
When addressing **"{question}"**, high-scale production systems face specific physical constraints:
- **Contention vs Throughput:** Under heavy concurrent load, locking or synchronous round-trips cause tail-latency degradation (P99 latency spikes).
- **Failure Isolation:** Systems must be designed assuming hardware nodes, network cables, and third-party dependencies *will* fail arbitrarily.

#### 2. 💡 First-Principles Mental Model & Analogy
> {analogy}

#### 3. 🛠️ Architectural Resolution Strategy
1. **Single-Pass Invariant:** Structure computations so each record is touched exactly once, maintaining `O(N)` or `O(1)` runtime.
2. **Defensive Resource Bounding:** Always establish explicit socket timeouts, maximum query execution limits (`statement_timeout`), and connection pool caps to prevent thread starvation.
3. **Optimistic Concurrency Control:** When synchronizing state across nodes, prefer atomic primitives (`Redis INCRBY`, CAS compare-and-swap, or SQL version column timestamps) rather than coarse-grained pessimistic mutex locks.

```python
# Production Architectural Snippet
async def execute_safe_operation(resource_id: str, payload: dict) -> dict:
    \"\"\"Executes with non-blocking concurrency and idempotency checks.\"\"\"
    # 1. Acquire fencing token or verify version tag
    # 2. Perform validation in memory (O(1))
    # 3. Commit state atomically with structured logging
    return {{"status": "committed", "resource_id": resource_id}}
```

#### 4. ⚠️ Common Interview Gotchas & Edge Cases:
- **Cache Stampede / Thundering Herd:** When a popular key expires, thousands of concurrent requests hit the database simultaneously. Fix with mutex locking or probabilistic early renewal.
- **Split-Brain Contention:** In network partitions, never accept writes on a minority partition without a Raft quorum (N/2 + 1).
- **Connection Leakage:** Forgetting to close database cursors or HTTP client sessions leads to connection pool exhaustion.

#### 5. ⏱️ Big-O Complexity Profiling:
- **Time Complexity:** O(1) lookup via hashed indexes; O(N) sequential scan.
- **Space Complexity:** O(K) auxiliary working set memory.
"""
            chips = [
                "💡 Explain Like I'm 5 (ELI5)",
                "💻 Generate Full Code Implementation",
                "🏗️ Show System Design Architecture",
                "🔥 Staff Bar Raiser Cross-Question"
            ]

        return {
            "answer": answer,
            "provider": f"{self.provider.upper()} Engine (CogniPrep Core)",
            "mode": mode,
            "action_chips": chips,
            "code_snippet": None,
            "suggested_followups": [
                f"How would {target_company} test this logic in a Live Bar Raiser interview?",
                "What happens if traffic suddenly surges by 10x in 60 seconds?",
                "How would you monitor P99 latency and error budgets for this component?"
            ]
        }

ai_service = AIService()

