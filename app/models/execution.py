from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from app.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=True)
    execution_type = Column(String(50), nullable=False) # "python" or "sql"
    code_content = Column(Text, nullable=False)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    execution_time_ms = Column(Float, default=0.0)
    query_plan = Column(JSON, default=list) # For SQL EXPLAIN results
    created_at = Column(DateTime, default=utc_now)
