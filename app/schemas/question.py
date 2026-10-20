from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.question import QuestionCategory, QuestionDifficulty

class QuestionBase(BaseModel):
    title: str
    slug: str
    category: str
    difficulty: str
    min_exp_years: int = 0
    max_exp_years: int = 15
    company_tags: List[str] = []
    frequency_score: int = 80
    mindmap_topic: Optional[str] = None
    mindmap_node: Optional[str] = None
    scenario_text: str
    theory_explanation: Optional[str] = None
    has_python_sandbox: bool = True
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    test_cases_json: List[Dict[str, Any]] = []
    has_sql_sandbox: bool = False
    sql_schema: Optional[str] = "ecommerce"
    starter_sql: Optional[str] = None
    solution_sql: Optional[str] = None
    has_redis_sandbox: bool = False
    starter_redis: Optional[str] = None
    solution_redis: Optional[str] = None
    has_nosql_sandbox: bool = False
    starter_nosql: Optional[str] = None
    solution_nosql: Optional[str] = None
    cross_questions: List[str] = []
    common_traps: List[str] = []
    best_practices: List[str] = []
    phase: Optional[str] = "basic"
    mcq_question: Optional[str] = None
    mcq_options: List[str] = []
    mcq_correct_index: Optional[int] = 0
    mcq_explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionSummary(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    difficulty: str
    min_exp_years: int
    max_exp_years: int
    company_tags: List[str]
    frequency_score: int
    mindmap_topic: Optional[str]
    has_python_sandbox: bool
    has_sql_sandbox: bool
    has_redis_sandbox: bool = False
    has_nosql_sandbox: bool = False
    phase: Optional[str] = "basic"
    has_mcq: bool = False

    model_config = ConfigDict(from_attributes=True)

class QuestionDetail(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MCQVerifyRequest(BaseModel):
    question_id: int
    selected_index: int

class MCQVerifyResponse(BaseModel):
    is_correct: bool
    correct_index: int
    explanation: str
    question_id: int

class MCQQuizItem(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    difficulty: str
    phase: str
    company_tags: List[str] = []
    mcq_question: str
    mcq_options: List[str]

