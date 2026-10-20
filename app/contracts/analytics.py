from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

class AnalyticsServiceContract(ABC):
    """Contract for platform telemetry, execution logs, and analytics."""
    
    @abstractmethod
    def get_system_stats(self, db: Session) -> Dict[str, Any]:
        """Calculates global platform statistics, ecosystem counts, and active tracks."""
        pass

    @abstractmethod
    def log_execution(
        self,
        execution_type: str,
        code_content: str,
        stdout: Optional[str],
        stderr: Optional[str],
        success: bool,
        execution_time_ms: float,
        db: Session
    ) -> None:
        """Records an execution telemetry event into storage asynchronously."""
        pass
