from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.container import get_mindmap_service
from app.contracts.mindmap import MindmapServiceContract
from app.schemas.mindmap import MindmapTopicResponse

router = APIRouter(prefix="/mindmaps", tags=["Theoretical Mindmaps"])

@router.get("", response_model=List[MindmapTopicResponse])
def list_mindmaps(
    db: Session = Depends(get_db),
    mindmap_svc: MindmapServiceContract = Depends(get_mindmap_service)
):
    """Returns architecture roadmap topics with Mermaid flowchart specifications."""
    return mindmap_svc.get_topics(db=db)

@router.get("/{slug}", response_model=MindmapTopicResponse)
def get_mindmap(
    slug: str,
    db: Session = Depends(get_db),
    mindmap_svc: MindmapServiceContract = Depends(get_mindmap_service)
):
    """Retrieves deep architectural breakdown and system internals for a topic."""
    topic = mindmap_svc.get_topic_by_slug(slug, db=db)
    if not topic:
        raise HTTPException(status_code=404, detail="Mindmap topic not found")
    return topic
