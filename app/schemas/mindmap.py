from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class MindmapNodeDetail(BaseModel):
    id: str
    label: str
    summary: str
    mnc_importance: str
    depth_level: str # junior, mid, senior
    code_sample: Optional[str] = None
    common_traps: List[str] = []
    interview_cross_questions: List[str] = []

class MindmapTopicResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    category: str
    order_index: int
    mermaid_diagram: Optional[str]
    nodes: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)
