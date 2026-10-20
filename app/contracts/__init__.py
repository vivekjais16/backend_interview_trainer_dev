from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

# Re-export all domain contracts
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

__all__ = [
    "CodeExecutionContract",
    "DatabaseExecutionContract",
    "CacheExecutionContract",
    "DocumentExecutionContract",
    "AIEvaluationContract",
    "QuestionServiceContract",
    "InterviewSessionContract",
    "MindmapServiceContract",
    "AnalyticsServiceContract",
]
