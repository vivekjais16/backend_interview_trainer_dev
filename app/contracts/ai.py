from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIEvaluationContract(ABC):
    """Contract for AI Bar Raiser interview assessment and follow-up generation."""
    
    @abstractmethod
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
        """Evaluates candidate response and generates score, feedback, and cross-questions."""
        pass
