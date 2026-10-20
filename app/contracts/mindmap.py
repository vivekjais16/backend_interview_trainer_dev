from abc import ABC, abstractmethod
from typing import List, Optional, Any
from sqlalchemy.orm import Session

class MindmapServiceContract(ABC):
    """Contract for interactive architecture mindmaps and visual roadmap graphs."""
    
    @abstractmethod
    def get_topics(self, db: Optional[Session] = None) -> List[Any]:
        """Returns all knowledge roadmap topics."""
        pass

    @abstractmethod
    def get_topic_by_slug(self, slug: str, db: Optional[Session] = None) -> Any:
        """Returns deep architecture nodes and Mermaid diagram for a topic slug."""
        pass
