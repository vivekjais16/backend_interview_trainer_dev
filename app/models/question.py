import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class QuestionCategory(str, enum.Enum):
    PYTHON_INTERNALS = "python_internals"
    ASYNC_CONCURRENCY = "async_concurrency"
    FASTAPI_ARCHITECTURE = "fastapi_architecture"
    POSTGRES_MYSQL = "postgres_mysql"
    SQL_DATABASE_INTERNALS = "sql_database_internals"
    MONGODB_NOSQL = "mongodb_nosql"
    REDIS_CACHING = "redis_caching"
    KAFKA_MESSAGING = "kafka_messaging"
    CELERY_RABBITMQ = "celery_rabbitmq"
    DOCKER_CONTAINERS = "docker_containers"
    KUBERNETES_DEVOPS = "kubernetes_devops"
    CICD_PIPELINES = "cicd_pipelines"
    SYSTEM_DESIGN_MNC = "system_design_mnc"
    PRODUCTION_TROUBLESHOOTING = "production_troubleshooting"
    GEN_AI = "gen_ai"
    RAG_SYSTEMS = "rag_systems"
    LLM_INFERENCE = "llm_inference"
    VECTOR_DATABASES = "vector_databases"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    SQL_OPTIMIZATION = "sql_optimization"
    NOSQL_DISTRIBUTED = "nosql_distributed"

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
    category = Column(String(80), index=True, nullable=False)
    difficulty = Column(String(50), index=True, nullable=False)
    min_exp_years = Column(Integer, default=0, index=True)
    max_exp_years = Column(Integer, default=15)
    
    # MNC Targeting
    company_tags = Column(JSON, default=list) # e.g. ["Amazon", "Uber", "Microsoft", "Stripe", "Netflix"]
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

    # SQL / NoSQL / Redis Sandbox Content
    has_sql_sandbox = Column(Boolean, default=False)
    sql_schema = Column(String(50), default="ecommerce") # ecommerce, fintech, hr_tech, postgres_jsonb
    starter_sql = Column(Text, nullable=True)
    solution_sql = Column(Text, nullable=True)

    # Interactive Domain Sandboxes
    has_redis_sandbox = Column(Boolean, default=False)
    starter_redis = Column(Text, nullable=True)
    solution_redis = Column(Text, nullable=True)

    has_nosql_sandbox = Column(Boolean, default=False)
    starter_nosql = Column(Text, nullable=True)
    solution_nosql = Column(Text, nullable=True)

    # Deep MNC Interviewer Cross Questions & Gotchas
    cross_questions = Column(JSON, default=list) # Array of follow-up deep probing questions
    common_traps = Column(JSON, default=list)    # Common mistakes candidates make
    best_practices = Column(JSON, default=list)  # Industry standards (P99 latency, ACID, caching)

    # Phase Progression & Interactive MCQ Assessment
    phase = Column(String(50), default="basic", index=True) # basic, intermediate, advanced
    mcq_question = Column(Text, nullable=True)
    mcq_options = Column(JSON, default=list) # 4 distinct choices: ["A) ...", "B) ...", "C) ...", "D) ..."]
    mcq_correct_index = Column(Integer, default=0) # 0-indexed correct option
    mcq_explanation = Column(Text, nullable=True) # Plain-English explanation

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
