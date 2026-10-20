from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.config import settings
from app.models.execution import ExecutionLog
from app.schemas.execution import SQLRunRequest, SQLRunResponse
from app.services.sql_runner import run_sql_query

router = APIRouter(prefix="/sandbox/sql", tags=["SQL Sandbox"])

@router.post("", response_model=SQLRunResponse)
def execute_sql_sandbox(payload: SQLRunRequest, db: Session = Depends(get_db)):
    result = run_sql_query(
        query=payload.query,
        schema_name=payload.schema_name or "ecommerce",
        include_explain=payload.include_explain,
        max_rows=settings.SQL_MAX_ROWS
    )

    # Log execution in DB
    try:
        log = ExecutionLog(
            execution_type="sql",
            code_content=payload.query,
            stdout=f"Rows: {result['row_count']}",
            stderr=result.get("error"),
            success=result["success"],
            execution_time_ms=result["execution_time_ms"],
            query_plan=result.get("query_plan", [])
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return result

@router.get("/schemas")
def get_sql_schemas_metadata() -> Dict[str, Any]:
    return {
        "schemas": [
            {
                "id": "ecommerce",
                "name": "E-Commerce & Orders",
                "description": "Amazon/Flipkart-style schema with customers, products, orders, order_items and indexes.",
                "tables": ["customers", "products", "orders", "order_items"]
            },
            {
                "id": "fintech",
                "name": "FinTech Payments & Ledger",
                "description": "Stripe/PayPal-style double-entry bookkeeping with accounts, transactions and idempotency keys.",
                "tables": ["accounts", "transactions"]
            },
            {
                "id": "hr_tech",
                "name": "HR & Employee Analytics",
                "description": "Enterprise hierarchy with departments, employees, salaries, and performance reviews.",
                "tables": ["departments", "employees", "performance_reviews"]
            }
        ]
    }
