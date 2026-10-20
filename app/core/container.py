from typing import Optional
from app.contracts.execution import (
    CodeExecutionContract,
    DatabaseExecutionContract,
    CacheExecutionContract,
    DocumentExecutionContract
)
from app.contracts.ai import AIEvaluationContract
from app.contracts.questions import QuestionServiceContract
from app.contracts.interview import InterviewSessionContract
from app.contracts.mindmap import MindmapServiceContract
from app.contracts.analytics import AnalyticsServiceContract

from app.services.python_runner import python_execution_service
from app.services.sql_runner import sql_execution_service
from app.services.redis_runner import redis_execution_service
from app.services.nosql_runner import nosql_execution_service
from app.services.ai_service import ai_service
from app.services.question_service import question_service
from app.services.interview_service import interview_service
from app.services.mindmap_service import mindmap_domain_service
from app.services.analytics_service import analytics_service
from app.core.events import event_dispatcher, EventDispatcher

class ServiceContainer:
    """
    Decoupled Inversion of Control (IoC) Service Container.
    Holds decoupled microservice adapters and enables zero-downtime swappability:
    If a component is moved to an independent remote microservice or replaced with
    a different backend, only its registration in this container needs to be updated.
    """
    def __init__(self):
        self.code_execution: CodeExecutionContract = python_execution_service
        self.database_execution: DatabaseExecutionContract = sql_execution_service
        self.cache_execution: CacheExecutionContract = redis_execution_service
        self.document_execution: DocumentExecutionContract = nosql_execution_service
        self.ai_evaluation: AIEvaluationContract = ai_service
        self.questions: QuestionServiceContract = question_service
        self.interviews: InterviewSessionContract = interview_service
        self.mindmaps: MindmapServiceContract = mindmap_domain_service
        self.analytics: AnalyticsServiceContract = analytics_service
        self.events: EventDispatcher = event_dispatcher

    def override_code_execution(self, service: CodeExecutionContract):
        self.code_execution = service

    def override_ai_evaluation(self, service: AIEvaluationContract):
        self.ai_evaluation = service
        if hasattr(self.interviews, "set_ai_evaluator"):
            self.interviews.set_ai_evaluator(service)

    def override_database_execution(self, service: DatabaseExecutionContract):
        self.database_execution = service

    def override_question_service(self, service: QuestionServiceContract):
        self.questions = service

# Global Container instance
container = ServiceContainer()

# ----------------------------------------------------
# FastAPI Dependency Injection Providers
# ----------------------------------------------------
def get_code_execution_service() -> CodeExecutionContract:
    return container.code_execution

def get_database_execution_service() -> DatabaseExecutionContract:
    return container.database_execution

def get_cache_execution_service() -> CacheExecutionContract:
    return container.cache_execution

def get_document_execution_service() -> DocumentExecutionContract:
    return container.document_execution

def get_ai_evaluation_service() -> AIEvaluationContract:
    return container.ai_evaluation

def get_question_service() -> QuestionServiceContract:
    return container.questions

def get_interview_service() -> InterviewSessionContract:
    return container.interviews

def get_mindmap_service() -> MindmapServiceContract:
    return container.mindmaps

def get_analytics_service() -> AnalyticsServiceContract:
    return container.analytics

def get_event_dispatcher() -> EventDispatcher:
    return container.events
