from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.mindmap import MindmapTopic
from app.schemas.mindmap import MindmapTopicResponse
from app.services.mindmap_service import get_all_mindmaps, get_mindmap_by_slug

router = APIRouter(prefix="/mindmaps", tags=["Theoretical Mindmaps"])

@router.get("", response_model=List[MindmapTopicResponse])
def list_mindmaps(db: Session = Depends(get_db)):
    topics = db.query(MindmapTopic).order_by(MindmapTopic.order_index.asc()).all()
    if not topics:
        # Fallback to in-memory data if not yet seeded in DB
        return get_all_mindmaps()
    return topics

@router.get("/{slug}", response_model=MindmapTopicResponse)
def get_mindmap(slug: str, db: Session = Depends(get_db)):
    topic = db.query(MindmapTopic).filter(MindmapTopic.slug == slug).first()
    if not topic:
        mem_topic = get_mindmap_by_slug(slug)
        if mem_topic:
            return mem_topic
        raise HTTPException(status_code=404, detail="Mindmap topic not found")
    return topic
