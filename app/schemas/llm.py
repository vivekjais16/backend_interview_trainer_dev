from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LLMAskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="The custom technical question, interview problem, or code scenario")
    code_context: Optional[str] = Field(None, description="Optional attached code or SQL snippet")
    mode: str = Field(default="comprehensive", description="comprehensive, eli5, code_solution, system_design, debug_edge_cases, bar_raiser_grill, generate_quiz")
    target_company: str = Field(default="Google", description="Target company to calibrate the response against")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Previous messages in chat session")

class LLMAskResponse(BaseModel):
    answer: str
    provider: str
    mode: str
    action_chips: List[str] = []
    code_snippet: Optional[str] = None
    suggested_followups: List[str] = []

class LLMPreset(BaseModel):
    title: str
    category: str
    prompt: str
    code_sample: Optional[str] = None
