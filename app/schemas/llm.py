from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LLMAskRequest(BaseModel):
    question: Optional[str] = Field(None, description="The custom technical question, interview problem, or code scenario")
    prompt: Optional[str] = Field(None, description="Alias for question")
    code_context: Optional[str] = Field(None, description="Optional attached code or SQL snippet")
    mode: str = Field(default="comprehensive", description="comprehensive, eli5, code_solution, system_design, debug_edge_cases, bar_raiser_grill, generate_quiz")
    target_company: str = Field(default="Accenture", description="Target company to calibrate the response against")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Previous messages in chat session")

class LLMAskResponse(BaseModel):
    answer: str
    answer_markdown: Optional[str] = None
    provider: str
    model_used: Optional[str] = None
    mode: str
    action_chips: List[str] = []
    code_snippet: Optional[str] = None
    suggested_followups: List[str] = []
    follow_up_questions: List[str] = []
    key_invariants: List[str] = []
    distractor_traps: List[str] = []

class LLMPreset(BaseModel):
    title: str
    category: str
    prompt: str
    code_sample: Optional[str] = None
