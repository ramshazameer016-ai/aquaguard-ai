"""Pydantic schemas package for AquaGuard AI."""

from pydantic import BaseModel
from typing import Optional, List

from backend.app.schemas.report import (
    ReportCategory,
    ReportCreate,
    ReportCreateResponse,
    ReportResponse,
    ReportListResponse,
)
from backend.app.schemas.event import (
    EventResponse,
    EventListResponse,
)


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    environment: Optional[str] = None


class DatabaseHealthResponse(BaseModel):
    """Database connectivity and PostGIS status response schema."""

    status: str
    connected: bool
    database: str
    postgis_enabled: bool
    postgis_version: Optional[str] = None
    tables: List[str] = []
    error: Optional[str] = None


__all__ = [
    "HealthResponse",
    "DatabaseHealthResponse",
    "ReportCategory",
    "ReportCreate",
    "ReportCreateResponse",
    "ReportResponse",
    "ReportListResponse",
    "EventResponse",
    "EventListResponse",
]
