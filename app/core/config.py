import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AI Python Backend & MNC Interview Trainer"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:rootpassword@localhost:3306/interview_trainer",
        description="MySQL connection string or fallback SQLite"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./interview_trainer.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_AUTO_FALLBACK_SQLITE: bool = True

    # GenAI Engine
    AI_PROVIDER: str = "mock"  # "mock", "gemini", "openai", "ollama"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    # Sandbox Limits
    CODE_EXECUTION_TIMEOUT_SECONDS: int = 5
    MAX_EXECUTION_MEMORY_MB: int = 128
    SQL_MAX_ROWS: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

