from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

class InterviewSessionContract(ABC):
    """Contract for multi-turn interview session orchestrator."""
    
    @abstractmethod
    def create_session(
        self,
        candidate_id: Optional[int],
        session_title: str,
        experience_level: str,
        target_company: Optional[str],
        db: Session
    ) -> Any:
        """Initializes a new candidate mock interview session."""
        pass

    @abstractmethod
    def get_session(self, session_id: int, db: Session) -> Any:
        """Fetches active session details and turn history."""
        pass

    @abstractmethod
    async def process_turn(
        self,
        session_id: int,
        question_id: Optional[int],
        candidate_response: Optional[str],
        candidate_code: Optional[str],
        candidate_sql: Optional[str],
        db: Session
    ) -> Any:
        """Coordinates turn evaluation, AI grading, and turn persistence."""
        pass
