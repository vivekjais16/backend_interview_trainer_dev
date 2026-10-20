from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class CodeExecutionContract(ABC):
    """Contract for sandboxed Python code execution and AST complexity analysis."""
    
    @abstractmethod
    def execute(self, code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
        """Executes Python code in a safe sandbox."""
        pass

    @abstractmethod
    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Performs static AST Big-O time and space complexity inspection."""
        pass

class DatabaseExecutionContract(ABC):
    """Contract for relational SQL database execution and query plan inspection."""
    
    @abstractmethod
    def execute(self, query: str, schema_name: str = "ecommerce", include_explain: bool = True, max_rows: int = 50) -> Dict[str, Any]:
        """Executes SQL query against the specified schema sandbox."""
        pass

    @abstractmethod
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Returns the available SQL schemas and their metadata."""
        pass

class CacheExecutionContract(ABC):
    """Contract for in-memory Redis cache execution and command emulation."""
    
    @abstractmethod
    def execute(self, script: str) -> Dict[str, Any]:
        """Executes multi-line Redis CLI commands and returns structured logs."""
        pass

class DocumentExecutionContract(ABC):
    """Contract for NoSQL / MongoDB aggregation pipeline execution."""
    
    @abstractmethod
    def execute(self, query_str: str) -> Dict[str, Any]:
        """Executes MongoDB query or aggregation pipeline against document collections."""
        pass
