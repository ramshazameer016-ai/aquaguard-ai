"""Application Settings for AquaGuard AI backend."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root and backend directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """AquaGuard AI Application Configuration."""

    APP_NAME: str = "AquaGuard AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # PostgreSQL + PostGIS database URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/aquaguard"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
