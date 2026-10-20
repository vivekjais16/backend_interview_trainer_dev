from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class PythonRunRequest(BaseModel):
    code: str = Field(..., description="Python script to run in sandbox")
    timeout_seconds: Optional[int] = 5
    question_id: Optional[int] = None

class PythonRunResponse(BaseModel):
    stdout: str
    stderr: str
    return_value: Optional[str] = None
    execution_time_ms: float
    success: bool
    test_results: Optional[List[Dict[str, Any]]] = None
    complexity_analysis: Optional[Dict[str, Any]] = None

class SQLRunRequest(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    schema_name: str = Field(default="ecommerce", description="ecommerce, fintech, hr_tech")
    include_explain: bool = True
    question_id: Optional[int] = None

class SQLRunResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float
    success: bool
    error: Optional[str] = None
    query_plan: Optional[List[Dict[str, Any]]] = None
