# Legacy function-level runners (100% backward compatibility)
from app.services.python_runner import run_python_code, analyze_code_complexity, python_execution_service, PythonExecutionService
from app.services.sql_runner import run_sql_query, sql_execution_service, SQLExecutionService
from app.services.redis_runner import run_redis_commands, redis_execution_service, RedisExecutionService
from app.services.nosql_runner import run_nosql_query, nosql_execution_service, NoSQLExecutionService
from app.services.ai_service import ai_service, AIService
from app.services.mindmap_service import get_all_mindmaps, get_mindmap_by_slug, mindmap_domain_service, MindmapDomainService
from app.services.question_service import question_service, QuestionDomainService
from app.services.interview_service import interview_service, InterviewSessionDomainService
from app.services.analytics_service import analytics_service, AnalyticsDomainService

__all__ = [
    # Functions
    "run_python_code",
    "analyze_code_complexity",
    "run_sql_query",
    "run_redis_commands",
    "run_nosql_query",
    "get_all_mindmaps",
    "get_mindmap_by_slug",
    # Service Instances
    "python_execution_service",
    "sql_execution_service",
    "redis_execution_service",
    "nosql_execution_service",
    "ai_service",
    "mindmap_domain_service",
    "question_service",
    "interview_service",
    "analytics_service",
    # Service Classes
    "PythonExecutionService",
    "SQLExecutionService",
    "RedisExecutionService",
    "NoSQLExecutionService",
    "AIService",
    "MindmapDomainService",
    "QuestionDomainService",
    "InterviewSessionDomainService",
    "AnalyticsDomainService",
]
