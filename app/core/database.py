import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    target_url = settings.DATABASE_URL
    is_sqlite = target_url.startswith("sqlite")

    try:
        if is_sqlite:
            engine = create_engine(
                target_url,
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(
                target_url,
                pool_pre_ping=True,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW
            )
        # Verify connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to primary database: {target_url.split('@')[-1] if '@' in target_url else target_url}")
        return engine, False
    except Exception as exc:
        if settings.DB_AUTO_FALLBACK_SQLITE:
            logger.warning(
                f"Could not connect to primary database ({exc}). "
                f"Falling back to local SQLite: {settings.SQLITE_FALLBACK_URL}"
            )
            engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
            return engine, True
        raise exc

engine, is_fallback_sqlite = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import base
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas initialized.")
