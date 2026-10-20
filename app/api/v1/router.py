from fastapi import APIRouter
from app.api.v1.questions import router as questions_router
from app.api.v1.code_runner import router as code_runner_router
from app.api.v1.sql_runner import router as sql_runner_router
from app.api.v1.interview import router as interview_router
from app.api.v1.mindmap import router as mindmap_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(questions_router)
api_v1_router.include_router(code_runner_router)
api_v1_router.include_router(sql_runner_router)
api_v1_router.include_router(interview_router)
api_v1_router.include_router(mindmap_router)
api_v1_router.include_router(analytics_router)
