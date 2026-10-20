from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal, is_fallback_sqlite
from app.seeds.runner import seed_database
from app.api.v1.router import api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("interview_trainer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed data
    logger.info("Initializing database schemas...")
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    
    db_mode = "SQLite (Local Fallback)" if is_fallback_sqlite else "MySQL (Production)"
    logger.info(f"AI Interview Trainer platform started successfully with {db_mode}.")
    yield
    # Shutdown
    logger.info("Shutting down AI Interview Trainer platform.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Interactive Jupyter-style AI Backend Interview Trainer with Python Interpreter, SQL Compiler, Mindmaps & Adaptive MNC Grilling.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Mount API Router
app.include_router(api_v1_router)

@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "db_mode": "SQLite (Local Auto-Fallback)" if is_fallback_sqlite else "MySQL (Production)",
        "ai_provider": settings.AI_PROVIDER
    })
