from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class MindmapTopic(Base):
    __tablename__ = "mindmap_topics"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True)
    order_index = Column(Integer, default=0)
    mermaid_diagram = Column(Text, nullable=True)
    nodes = Column(JSON, default=list) # Array of detailed subnodes
    created_at = Column(DateTime, default=utc_now)
