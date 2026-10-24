from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal, is_fallback_sqlite
from app.core.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    PayloadLimitMiddleware,
    secure_db_file_permissions
)
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
    
    # Secure SQLite database file permissions (0600) to prevent OS-level tampering
    secure_db_file_permissions("./interview_trainer.db")

    db_mode = "SQLite (Local Fallback)" if is_fallback_sqlite else "MySQL (Production)"
    logger.info(f"AI Interview Trainer platform started successfully with {db_mode}.")
    yield
    # Shutdown
    logger.info("Shutting down AI Interview Trainer platform.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Interactive Jupyter-style AI Backend Interview Trainer with Python Interpreter, SQL Compiler, Mindmaps & Adaptive MNC Grilling.",
    version="2.0.0",
    lifespan=lifespan
)

# 1. Payload Size Limiter (Blocks buffer-overflow / memory-exhaustion attacks > 512KB)
app.add_middleware(PayloadLimitMiddleware)

# 2. Rate Limiting Middleware (Guards sandboxes against brute-force & denial of service)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

# 3. Security Headers Middleware (X-Content-Type-Options, X-Frame-Options, CSP, Referrer-Policy)
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Static and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

from fastapi.responses import HTMLResponse, Response

# Mount API Router
app.include_router(api_v1_router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="#6366f1"/><text x="50%" y="55%" font-size="55" font-family="sans-serif" font-weight="900" fill="#ffffff" dominant-baseline="central" text-anchor="middle">⚡</text></svg>"""
    return Response(content=svg_icon, media_type="image/svg+xml")

@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "db_mode": "SQLite (Local Auto-Fallback)" if is_fallback_sqlite else "MySQL (Production)",
            "ai_provider": settings.AI_PROVIDER
        }
    )

