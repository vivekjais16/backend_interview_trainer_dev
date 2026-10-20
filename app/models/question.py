import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Boolean
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class QuestionCategory(str, enum.Enum):
    PYTHON_INTERNALS = "python_internals"
    ASYNC_CONCURRENCY = "async_concurrency"
    FASTAPI_ARCHITECTURE = "fastapi_architecture"
    SQL_DATABASE_INTERNALS = "sql_database_internals"
    SYSTEM_DESIGN_MNC = "system_design_mnc"
    PRODUCTION_TROUBLESHOOTING = "production_troubleshooting"

class QuestionDifficulty(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ARCHITECT = "architect"

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(Enum(QuestionCategory), index=True, nullable=False)
    difficulty = Column(Enum(QuestionDifficulty), index=True, nullable=False)
    min_exp_years = Column(Integer, default=0, index=True)
    max_exp_years = Column(Integer, default=15)
    
    # MNC Targeting
    company_tags = Column(JSON, default=list) # e.g. ["Amazon", "Uber", "Microsoft", "Stripe"]
    frequency_score = Column(Integer, default=85) # High frequency MNC questions

    # Theoretical Mind Map connection
    mindmap_topic = Column(String(100), index=True)
    mindmap_node = Column(String(100))

    # Real-Time Scenario description
    scenario_text = Column(Text, nullable=False)
    theory_explanation = Column(Text, nullable=True)
    
    # Practical Sandbox Content
    has_python_sandbox = Column(Boolean, default=True)
    starter_code = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    test_cases_json = Column(JSON, default=list)

    # SQL Sandbox Content
    has_sql_sandbox = Column(Boolean, default=False)
    sql_schema = Column(String(50), default="ecommerce") # ecommerce, fintech, hr_tech
    starter_sql = Column(Text, nullable=True)
    solution_sql = Column(Text, nullable=True)

    # Deep MNC Interviewer Cross Questions & Gotchas
    cross_questions = Column(JSON, default=list) # Array of follow-up deep probing questions
    common_traps = Column(JSON, default=list)    # Common mistakes candidates make
    best_practices = Column(JSON, default=list)  # Industry standards (P99 latency, ACID, caching)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
