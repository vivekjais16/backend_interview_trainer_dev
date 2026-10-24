from fastapi import APIRouter
from app.api.v1.questions import router as questions_router
from app.api.v1.code_runner import router as code_runner_router
from app.api.v1.sql_runner import router as sql_runner_router
from app.api.v1.redis_runner import router as redis_runner_router
from app.api.v1.nosql_runner import router as nosql_runner_router
from app.api.v1.interview import router as interview_router
from app.api.v1.mindmap import router as mindmap_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.llm import router as llm_router

api_v1_router = APIRouter(prefix="/api/v1")

# Modular Microservices Gateway Routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(llm_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(questions_router)
api_v1_router.include_router(code_runner_router)
api_v1_router.include_router(sql_runner_router)
api_v1_router.include_router(redis_runner_router)
api_v1_router.include_router(nosql_runner_router)
api_v1_router.include_router(interview_router)
api_v1_router.include_router(mindmap_router)
api_v1_router.include_router(analytics_router)
