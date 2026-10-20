from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

class QuestionServiceContract(ABC):
    """Contract for Question Catalog, MCQ verification, and career phase progression."""
    
    @abstractmethod
    def list_questions(
        self,
        phase: Optional[str] = None,
        experience_years: Optional[int] = None,
        experience_level: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
        most_asked: Optional[bool] = None,
        db: Session = None
    ) -> List[Any]:
        """Filters and retrieves questions matching criteria."""
        pass

    @abstractmethod
    def get_most_asked_questions(self, limit: int = 50, db: Session = None) -> List[Any]:
        """Retrieves top-priority most-asked MNC interview questions."""
        pass

    @abstractmethod
    def get_concepts(self) -> List[Dict[str, Any]]:
        """Retrieves centralized concept reference guide (InterviewBit & GFG style)."""
        pass

    @abstractmethod
    def get_question(self, question_id: int, db: Session) -> Any:
        """Retrieves a single question by primary ID."""
        pass

    @abstractmethod
    def get_mcq_quiz(self, phase: Optional[str], db: Session) -> List[Dict[str, Any]]:
        """Retrieves randomized MCQ assessment items for speed arena."""
        pass

    @abstractmethod
    def verify_mcq(self, question_id: int, selected_index: int, db: Session) -> Dict[str, Any]:
        """Validates option selection and provides immediate explanation."""
        pass
