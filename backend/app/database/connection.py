"""Database connection and session management for AquaGuard AI."""

import logging
from typing import Generator, Dict, Any, Tuple
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.app.config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()

# SQLAlchemy Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def enable_postgis_extension() -> bool:
    """Ensure PostGIS extension is created in the database."""
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            return True
    except Exception as exc:
        logger.warning("Could not execute CREATE EXTENSION IF NOT EXISTS postgis: %s", exc)
        return False


def check_db_connection() -> Dict[str, Any]:
    """Check connectivity to PostgreSQL and verify PostGIS extension status."""
    result: Dict[str, Any] = {
        "connected": False,
        "database": "postgresql",
        "postgis_enabled": False,
        "postgis_version": None,
        "tables": [],
        "error": None,
    }

    try:
        with engine.connect() as conn:
            # 1. Connectivity check
            conn.execute(text("SELECT 1;"))
            result["connected"] = True

            # 2. PostGIS check
            try:
                pgis_res = conn.execute(text("SELECT PostGIS_Version();")).scalar()
                result["postgis_enabled"] = True
                result["postgis_version"] = str(pgis_res)
            except Exception as pgis_err:
                result["postgis_enabled"] = False
                result["postgis_error"] = str(pgis_err)

            # 3. Existing tables check
            inspector = inspect(engine)
            result["tables"] = inspector.get_table_names()

    except Exception as exc:
        result["connected"] = False
        result["error"] = str(exc)

    return result


def init_db() -> None:
    """Initialize PostGIS extension and create all database tables."""
    enable_postgis_extension()
    Base.metadata.create_all(bind=engine)
