from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.question import QuestionCategory, QuestionDifficulty

class QuestionBase(BaseModel):
    title: str
    slug: str
    category: QuestionCategory
    difficulty: QuestionDifficulty
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
    cross_questions: List[str] = []
    common_traps: List[str] = []
    best_practices: List[str] = []

class QuestionCreate(QuestionBase):
    pass

class QuestionSummary(BaseModel):
    id: int
    title: str
    slug: str
    category: QuestionCategory
    difficulty: QuestionDifficulty
    min_exp_years: int
    max_exp_years: int
    company_tags: List[str]
    frequency_score: int
    mindmap_topic: Optional[str]
    has_python_sandbox: bool
    has_sql_sandbox: bool

    model_config = ConfigDict(from_attributes=True)

class QuestionDetail(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
