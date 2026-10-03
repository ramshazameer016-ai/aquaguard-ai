"""AquaGuard AI — Stage 2 FastAPI Application Entrypoint.

Explainable evidence fusion for citizen-reported water-health anomalies.

Stage 2: FastAPI Backend
"""

import logging

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config.settings import settings
from backend.app.database.connection import init_db, check_db_connection
from backend.app.api.reports import router as reports_router
from backend.app.api.events import router as events_router
from backend.app.api.evidence import router as evidence_router
from backend.app.api.environmental import router as environmental_router
from backend.app.api.correlation import router as correlation_router
from backend.app.api.ai import router as ai_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.verification import router as verification_router
from backend.app.api.one_health import router as one_health_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.risk import router as risk_router
from backend.app.api.actions import router as actions_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("aquaguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to initialize database and tables on startup."""
    logger.info("Initializing AquaGuard AI foundation...")

    try:
        init_db()
        logger.info("Database schema and PostGIS extension verified.")
    except Exception as exc:
        logger.warning(
            "Database initialization during startup failed: %s",
            exc,
        )

    yield

    logger.info("Shutting down AquaGuard AI application.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AquaGuard AI transforms citizen observations into evidence-backed "
        "water-health intelligence using explainable evidence fusion."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# Enable CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register Citizen Reports API
app.include_router(reports_router)
app.include_router(events_router)
app.include_router(evidence_router)
app.include_router(environmental_router)
app.include_router(correlation_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(verification_router)
app.include_router(one_health_router)
app.include_router(alerts_router)
app.include_router(risk_router)
app.include_router(actions_router)


@app.get("/health", status_code=status.HTTP_200_OK)
def get_health() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }


@app.get("/health/db", status_code=status.HTTP_200_OK)
def get_db_health() -> JSONResponse:
    """Database connectivity and PostGIS status endpoint."""
    db_status = check_db_connection()

    if db_status["connected"]:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "service": settings.APP_NAME,
                "database": db_status,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "error",
            "service": settings.APP_NAME,
            "database": db_status,
        },
    )


@app.get("/", status_code=status.HTTP_200_OK)
def get_root() -> Dict[str, Any]:
    """Root endpoint with service overview and scope boundaries."""
    return {
        "service": settings.APP_NAME,
        "stage": "Stage 2: FastAPI Backend",
        "tagline": "See it. Understand it. Verify it. Act on it.",
        "concept": (
            "Explainable evidence fusion for citizen-reported "
            "water-health anomalies."
        ),
        "rules": [
            "Citizen reports are raw evidence, not confirmed pollution.",
            "Evidence Confidence belongs to events, not citizens.",
            "Human verification is required for consequential decisions.",
            "Simulated data is always explicitly labelled.",
        ],
    }